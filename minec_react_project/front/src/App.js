import React, { Component } from 'react';
import './App.css';
import * as axios  from 'axios';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

const ReactTags = require('react-tag-autocomplete');

class FilterField extends Component{

  constructor(props){
    super(props);
    this.state = {
        pos_prop : Object.keys(props.ask_dict),
        data : 0,
        error : 'None',
    };
    this.state.data = {
            property: this.state.pos_prop[0],
            sign: "eq",
            value: "",
        };

    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.handleChangeSign = this.handleChangeSign.bind(this);
    this.handleChangeValue = this.handleChangeValue.bind(this);
    this.validateDate = this.validateDate.bind(this);
    this.validateNumberString = this.validateNumberString.bind(this);
  }

  handleChangeProperty(event){
      let data = this.state.data;
      data.property = event.target.value;
      if (this.props.ask_dict[data.property].suggestions.length > 0){
          data.value = Array(1);
          data.value[0] = this.props.ask_dict[data.property].suggestions[0];
      }
      this.setState({data : data});
      this.handleFilterChange();
  }

  handleChangeSign(event){
      let data = this.state.data;
      data.sign = event.target.value;
      this.setState({data : data});
      this.handleFilterChange();
  }

  handleChangeValue(event){
      let data = this.state.data;
      data.value = event.target.value;
      this.setState({data : data});
      this.handleFilterChange();
  }

  handleFilterChange = () => {
      this.props.onNewData(this.props.index, this.state.data);
  };

 handleDelete (i) {
    let data = this.state.data;
    data.value = data.value.slice(0);
    data.value.splice(i, 1);
    this.setState({ data : data })
  }

  handleAddition (tag) {
    let data = this.state.data;
    data.value = [].concat(data.value, tag);
    this.setState({ data : data })
  }


  validateDate(event){
     event.target.value.replace(' ', '');
     this.setState({error : 'None'});
     if (!event.target.value.match(/^\d{2}\-\d{2}\-\d{4}$/)){
        this.setState({error : "date must be 'XX-XX-XXXX'"})
     }

  }

  validateNumberString(event){
     event.target.value.replace(' ', '');
     this.setState({error : 'None'});
     if (!event.target.value.match(/^(\d+,|\d+\-\d+,)*(\d+|\d+\-\d+)$/)){
         this.setState({error :
                 "number string should consist of numbers and ranges" +
                 " separated by comma, like '12,23-34,234,250-800'"})
     }
  }

  render() {
    return(
      <div className="row">
        <select
            value={this.state.data.property}
            onSelect={this.handleChangeProperty}
            onChange={this.handleChangeProperty}
        >
            {this.state.pos_prop.map((item) => (
                    <option value={item}>
                        {this.props.ask_dict[item].human}
                    </option>

            ))}
        </select>
        <select
            value={this.state.data.sign}
            onSelect={this.handleChangeSign}
            onChange={this.handleChangeSign}
        >
          <option value="lt"> {"<"} </option>
          <option value="gt"> {">"} </option>
          <option value="eq"> {"="} </option>
          <option value="gte"> {">="} </option>
          <option value="lte"> {"<="} </option>
        </select>
        <label>
            {this.props.ask_dict[this.state.data.property].suggestions.length > 0 ? (
                <ReactTags
                    tags={this.state.data.value}
                    suggestions={this.props.ask_dict[this.state.data.property].suggestions}
                    handleDelete={this.handleDelete.bind(this)}
                    handleAddition={this.handleAddition.bind(this)}
                />

            ) : (<a></a>)}
            {this.props.ask_dict[this.state.data.property].type == 'int' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateNumberString}
                />
            ) : (<a></a>)}
            {this.props.ask_dict[this.state.data.property].type == 'date' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateDate}
                />
            ) : (<a></a>)}
        </label>
          {this.state.error == 'None' ? (<a></a>) : (
              <label>
                  {this.state.error}
              </label>

          )}

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
  };

  render() {
    return(
      <div>
        <div className="state">{this.state.app_state} </div>

        {
          this.state.filters.map((component, index) => (
              <FilterField
                  key={index}
                  index={index}
                  onNewData={this.handleChildChange}
                  ask_dict={this.props.ask_dict}
              >
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
              this.state.data[0][i].sign;
          if (Array.isArray(this.state.data[0][i].value)) {
              for (let temp = 0; temp < this.state.data[0][i].value.length; temp++){
                  params['filter_' + i] += '__' + this.state.data[0][i].value[temp].name;
              }
          }
          else{
                params['filter_' + i] += '__' + this.state.data[0][i].value;
          }
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
            <FilterController onNewData={this.handleChildChange} ask_dict={this.props.ask_dict}>
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

    constructor(props){
        super(props);
        this.state = {
            'ask_dict': Array(0),
        };
    }

    on_ASK_DICT_load(req){
        this.setState({
            'ask_dict': req.data.ask_dict,
        });
    }

    componentWillMount() {
        axios.get(
          'http://127.0.0.1:8000/api/get_ask_dict', {
          })
          .then((res) => this.on_ASK_DICT_load(res))
          .catch(function (error) {
              console.log(error);
          });
    }


    render() {
    return (
      <div>
        <div className="Title">Приложение взаимодействия с базами ФНС</div>
        <Main ask_dict={this.state.ask_dict}/>
      </div>
    );
  }
}

export default App;
