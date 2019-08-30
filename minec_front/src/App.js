import React, { Component } from 'react';
import './App.css';
import * as axios  from 'axios';

import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import { FilterController } from './filters';
import { AgregatorContorll } from './agregators';
import { GroupbyContorll } from './groupper';


//const addr = '127.0.0.1:8000';
const addr = '84.201.147.95';
//const addr = '0.0.0.0';


class Main extends Component {

  constructor(props){
      super(props);
      this.state = {
          data: Array(3),
          app_state: 'Ожидание запроса',
          is_file: false,
      };

      this.onFileLoadSelect = this.onFileLoadSelect.bind(this);
  }

  handleChildChange = (index, data) => {
      let buf = this.state.data.slice();
      buf[index] = data;
      this.setState({data : buf});
  };

  onLoadQuery(response){
    console.log(response);
    this.setState({
        table_header : JSON.parse(response.data.table_header),
        table_human_header : JSON.parse(response.data.table_human_header),
        table_body : JSON.parse(response.data.table_body),
        table_error : JSON.parse(response.data.table_error),
        app_state: 'Запрос получен. Ожидание нового запроса'
    });

    if (this.state.table_error.length > 0){
        this.setState({app_state : 'Запрос завершен с ошибками'})
    }
  }

  makeParamsForQuery(){
    // 0 - filters
      const spase = '___';
      const real_space = '|||';
      let params = {};
      if (Array.isArray(this.state.data[0])) {
          for (let i = 0; i < this.state.data[0].length; i++) {
              if (this.state.data[0][i].property === '---'){
                  continue;
              }
              params['filter_' + i] =
                  this.state.data[0][i].property + spase +
                  this.state.data[0][i].sign + spase;
              if (Array.isArray(this.state.data[0][i].value)) {
                  for (let temp = 0; temp < this.state.data[0][i].value.length; temp++) {
                      params['filter_' + i] += this.state.data[0][i].value[temp] + spase;
                  }
              } else {
                  params['filter_' + i] += this.state.data[0][i].value + spase;
              }
          }
      }
      // 1 - grouppers
      if (Array.isArray(this.state.data[1])) {
          for (let i = 0; i < this.state.data[1].length; i++) {
              if (this.state.data[1][i].property === '---'){
                  continue;
              }
              params['groupby_' + i] =
                  this.state.data[1][i].property;
          }
      }
      // 2 - aggregations
      if (Array.isArray(this.state.data[2])) {
          for (let i = 0; i < this.state.data[2].length; i++) {
              if (this.state.data[2][i].property === '---'){
                  continue;
              }
              params['aggregate_' + i] =
                  this.state.data[2][i].sign + spase +
                  this.state.data[2][i].property;
          }
      }

      return params;
  }

  showInfo(){
    alert('Это приложение взяиможействия с базами данных Федеральной налоговой службы.\n' +
        'Приложение поддерживает фильтрацию, группировки и агрегации. (Обертка над sql) ' +
        'Для добавления элемента (фильтра, группировки, агрегации) нажмите на соответствующую кнопку. ' +
        'Вначале применяется фильтрация, потом группировки, далее к каждой группе применяются все агрегации. ' +
        'В случае отсутствия группировок, агрегация применяется ко всем данным.\n\n' +
        'Так как в базе хранятся данные за многие промежутки времени, обязательным является либо ' +
        'фильтрация по дате записей, либо группировка по датам записей (Поле "дата обновления").' +
        'Чтобы посмотреть возможные даты записей нажмите кнопку "Показать даты обновлений"\n\n' +
        'Для получения информации о поле и формате данных нажмите на "?" выбрав поле в списке фильтров.')
  }

  getQuery(){
      this.setState({app_state : 'Запрос отправлен'});
      let params = this.makeParamsForQuery();

      if (!this.state.is_file) {
          axios.get(
              ''.concat('http://', addr, '/api/get'), {
                  params: params,
              })
              .then((res) => this.onLoadQuery(res))
              .catch(function (error) {
                  console.log(error);
              });
      }
      else{
          axios(''.concat('http://', addr, '/api/get/file/'), {
              params: params,
              method: 'GET',
              responseType: 'blob', // important
        }).then((response) => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'data.csv');
          document.body.appendChild(link);
          link.click();
        });
      }
  }


  onFileLoadSelect(){
    this.setState({is_file : !this.state.is_file})
  }

  get_update_date(){
    axios.get(
      ''.concat('http://', addr, '/api/get_updates_dates')
    )
      .then((res) => this.onLoadQuery(res))
      .catch(function (error) {
          console.log(error);
      });
    }

  render() {
    return (
        <div className="Main">
            <button onClick={() => this.showInfo()}>Справка</button>
            <button onClick={() => this.get_update_date()}>Показать даты обновлений</button>
            <p/>
            <label>
                {this.state.app_state}
            </label>
            <p/>
            <label>
            <input
                type="checkbox"
                checked={this.state.is_file}
                onChange={this.onFileLoadSelect}
            />
                Возвращать запрос файлом
            </label>
          <div className="Controllers">
            <FilterController onNewData={this.handleChildChange} ask_dict={this.props.ask_dict}/>
            <GroupbyContorll onNewData={this.handleChildChange} ask_dict={this.props.ask_dict}/>
            <AgregatorContorll onNewData={this.handleChildChange} ask_dict={this.props.ask_dict}/>
          </div>
          <button
              className="make_query"
              onClick={() => this.getQuery()}
          >
            Сформировать таблицу
          </button>
            {Array.isArray(this.state.table_error) && this.state.table_error.length > 0 ? (
                <div>
                    <label>Ошибки запроса:</label>
                    {
                        this.state.table_error.map( (item) =>
                            <label>
                                {item}
                            </label>
                        )
                    }
                </div>
            ) : (<a></a>)
            }


          <MyTable2
              table_human_header={this.state.table_human_header}
              table_header={this.state.table_header}
              table_body={this.state.table_body}
          />
        </div>
    );
  }
}

class MyTable2 extends Component{

    render_item(item){
        if (item === true){
            return (<TableCell> {"True"} </TableCell>)
        }
        if (item === false){
            return (<TableCell> {"False"} </TableCell>)
        }
        return (<TableCell> {item} </TableCell>)
    }

    render() {
        if (!Array.isArray(this.props.table_header)) {
            return (<a></a>)
        }

        return (
            <Table>
                <TableHead>
                    <TableRow>
                        {
                            this.props.table_human_header.map((head_name) =>
                                <TableCell>{head_name}</TableCell>
                            )
                        }
                    </TableRow>
                </TableHead>
                <TableBody>
                    {
                        this.props.table_body.map((row) =>
                            <TableRow>
                                {
                                    this.props.table_header.map((head_name) =>
                                        (this.render_item(row[head_name]))
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
            ''.concat('http://', addr,'/api/get_ask_dict'), {
          })
          .then((res) => this.on_ASK_DICT_load(res))
          .catch(function (error) {
              console.log(error);
          });
    }


    render() {
    return (
      <div style={{ margin: '32px 32px 32px 32px' }}>
        <div className="Title">Приложение взаимодействия с базами ФНС</div>
        <Main ask_dict={this.state.ask_dict}/>
      </div>
    );
  }
}

export default App;
