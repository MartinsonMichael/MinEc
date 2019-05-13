import React, { Component } from 'react';
import './App.css';
import * as axios  from 'axios';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { FilterController } from './filters';


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
