import React, { Component } from 'react';
import './App.css';
import * as axios  from 'axios';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';


class FilterField extends Component{

  constructor(props){
    super(props);
    this.state = {
      property : "",
      sign : "eq",
      value : "",
    };
    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.handleChangeSign = this.handleChangeSign.bind(this);
    this.handleChangeValue = this.handleChangeValue.bind(this);
  }

  handleChangeProperty(event){
    this.setState({property : event.target.value});
    this.handleChange();
  }

  handleChangeSign(event){
    this.setState({sign : event.target.value});
    this.handleChange();
  }

  handleChangeValue(event){
    this.setState({value : event.target.value});
    this.handleChange();
  }

  // sleep(ms) {
  //   ms += new Date().getTime();
  //   while (new Date() < ms){}
  // }

  handleChange = () => {
      this.props.onNewData(this.props.index, this.state);
  };

  render() {
    return(
      <div className="row">
        <label>
          Имя параметра :
          <input
              type="text"
              value={this.state.property}
              onInput={this.handleChangeProperty}
              onBlur={this.handleChange}
          />
        </label>
        <select
            value={this.state.sign}
            onChange={this.handleChangeSign}>
            onSelect={this.handleChangeSign}
            onBlur={this.handleChangeSign}
          <option value="lt"> {"<"} </option>
          <option value="gt"> {">"} </option>
          <option value="eq"> {"="} </option>
          <option value="gte"> {">="} </option>
          <option value="lte"> {"<="} </option>
        </select>
        <label>
          <input
              type="text"
              value={this.state.value}
              onChange={this.handleChangeValue}
              onBlur={this.handleChange}
          />
        </label>

      </div>
    );

  }
}

class FilterController extends Component{
  constructor(props){
    super(props);
    this.state = {
      app_state : "Waiting for query",
      filters : Array(0),
      data : Array(0),
    };

  }

  addFilter(){
    let buf = this.state.filters.slice();
    buf.push(FilterField);
    this.setState({filters : buf});
  }


  handleChildChange = (index, pp) => {
      let buf = this.state.data.slice();
      buf[index] = pp;
      this.setState({data : buf});
      this.props.onNewData(0, buf);
  }

  render() {
    return(
      <div>
        <div className="state">{this.state.app_state} </div>

        {
          this.state.filters.map((component, index) => (
              <FilterField key={index} index={index} onNewData={this.handleChildChange}>
                {component}
              </FilterField>
          ))
        }


        <button
            className="add_filter_button"
            onClick={() => this.addFilter()}
        >
          Добавить фильтр
        </button>
      </div>
    );
  }
}

class Main extends Component {

  constructor(props){
      super(props);
      this.state = {
          control_filter: FilterController,
          data: Array(3),

          table_header: Array(0),
          table_body: Array(0),
          table_pk: 'pk',
      };
  }

  handleChildChange = (index, data) => {
      let buf = this.state.data.slice();
      buf[index] = data;
      this.setState({data : buf});
  };

  onLoadQuery(response){
    console.log(response);
    this.setState({
        table_header : response.data.table_header,
        table_body : JSON.parse(response.data.table_body),
        table_pk : response.data.table_pk,
    });
  }

  makeParamsForQuery(){
    // 0 - filters
      let params = {};
      for (let i = 0; i < this.state.data[0].length; i++){
          params['filter_' + i] =
              this.state.data[0][i].property + "__" +
              this.state.data[0][i].sign + "__" +
              this.state.data[0][i].value;
      }

      return params;
  }

  getQuery(){
      let params = this.makeParamsForQuery();
      this.setState({buf : params});
      axios.get(
          'http://127.0.0.1:8000/api/get', {
              params: params,
          })
          .then((res) => this.onLoadQuery(res))
          .catch(function (error) {
              console.log(error);
          });
  }

  render() {
    return (
        <div className="Main">
          <div className="Controllers">
            <FilterController onNewData={this.handleChildChange}>
                {this.state.control_filter}
            </FilterController>
          </div>
          <button
              className="make_query"
              onClick={() => this.getQuery()}
          >
            Сформировать таблицу
          </button>
          <MyTable
              pk={this.state.table_pk}
              header={this.state.table_header}
              table={this.state.table_body}
          />
        </div>
    );
  }
}

class MyTable extends Component{
    render() {
        return (
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>
                            {this.props.pk}
                        </TableCell>
                        {
                            this.props.header.map((head_name) =>
                                <TableCell>{head_name}</TableCell>
                            )
                        }
                    </TableRow>
                </TableHead>
                <TableBody>
                    {
                        this.props.table.map((row) =>
                            <TableRow>
                                <TableCell>
                                    {row['pk']}
                                </TableCell>
                                {
                                    this.props.header.map((head_name) =>
                                        <TableCell>{row['fields'][head_name]}</TableCell>
                                    )
                                }
                            </TableRow>
                        )
                    }
                </TableBody>
            </Table>
        );
    }
}

class App extends Component {
  render() {
    return (
      <div>
        <div className="Title">Приложение взаимодействия с базами ФНС</div>
        <Main/>
      </div>
    );
  }
}

export default App;
