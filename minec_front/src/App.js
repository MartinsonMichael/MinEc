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
import {ClipLoader} from "react-spinners";


const streamSaver = window.streamSaver

// const addr = '127.0.0.1:8000';
const addr = '84.201.147.95';
// const addr = '0.0.0.0';
// const addr = 'backend';

const spase = '#';

const CHECK_TIMEOUT = 500;

function address_maker(line) {
    const address = `http://${addr}${line}`
    console.log(`send request to address: ${address}`)
    return address
}

class Main extends Component {

  constructor(props){
      super(props);
      this.state = {
          data: Array(3),
          app_state: 'Ожидание запроса',
          is_file: false,
          extraFields: [],

          showLoadTable: false,
          tableToLoad: 'Company',
          dateToLoadTable: '',

          ticket_id: undefined,
          ticked_with_file: undefined,
          timer_Id: undefined,
      };

      this.onFileLoadSelect = this.onFileLoadSelect.bind(this);
      this.renderExtraFields = this.renderExtraFields.bind(this);
      this.loadSingleTable = this.loadSingleTable.bind(this);
      this.onTicketRecieved = this.onTicketRecieved.bind(this);
      this.ticketChecker = this.ticketChecker.bind(this);
      this.contentLoader = this.contentLoader.bind(this);
      this.fileLoader = this.fileLoader.bind(this);
      this.onLoadQuery = this.onLoadQuery.bind(this);
  }

  handleChildChange = (index, data) => {
      let buf = this.state.data.slice();
      buf[index] = data;
      this.setState({data : buf});
  };

  onLoadQuery(response){
    this.setState({
        table_human_header : JSON.parse(response.data.table_human_header),
        table_body : JSON.parse(response.data.table_body),
    });
  }

  makeParamsForQuery(){
    // 0 - filters

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
                  this.state.data[2][i].property + spase +
                  this.state.data[2][i].sign;
          }
      }

      if (Array.isArray(this.state.extraFields)) {
          this.state.extraFields
              .filter(item => item !== 'del')
              .forEach((item, index) => {
                  params['extra_f_' + index.toString()] = item
              }
          )
      }
      if (this.state.is_file) {
          params['file'] = 'true'
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

  onTicketRecieved(response) {
      console.log(response.data.ticket)
      const timerId = setTimeout(
          this.ticketChecker,
          CHECK_TIMEOUT * (this.state.is_file ? 60 : 20),
          response.data.ticket
      )
      this.setState({ticket_id: response.data.ticket, timerId: timerId})
  }

  ticketChecker(ticket_id) {
      console.log('request ticket status')
      axios.get(
          ''.concat(address_maker('/api/ticket_status')), {
              params: {ticket_id: ticket_id},
              timeout: 10 * 1000,
          })
          .then(response => {
              const ticket_obj = response.data
              this.setState({app_state: ticket_obj.ticket_status})
              if (ticket_obj.ticket_status === 'ready') {
                  this.setState({app_state: 'Готово. Загрузка таблизы...'})
                  if (!this.state.is_file) {
                      this.contentLoader()
                  } else {
                      this.fileLoader()
                  }
                  this.setState({ticket_id: undefined})
              } else {
                  if (ticket_obj.ticket_status.slice(0, 5) !== 'error') {
                      setTimeout(this.ticketChecker, CHECK_TIMEOUT, ticket_id)
                  } else{
                      this.setState({ticket_id: undefined})
                  }
              }
          })
          .catch(error => {
              setTimeout(this.ticketChecker, CHECK_TIMEOUT, ticket_id)
          });
  }

  contentLoader() {
      axios.get(
          ''.concat(address_maker('/api/content')), {
              params: {ticket_id: this.state.ticket_id},
              timeout: 10 * 1000,
          })
          .then(this.onLoadQuery)
          .catch(function (error) {
              console.log(error);
          });
  }

  fileLoader(ticket_id) {
        // const fileStream = streamSaver.createWriteStream('data.csv', {
        //     size: 22, // (optional) Will show progress
        //     writableStrategy: undefined, // (optional)
        //     readableStrategy: undefined  // (optional)
        //   })

        console.log('start file load')

        axios(
              ''.concat(address_maker('/api/content')), {
              params: {ticket_id: ticket_id},
              timeout: 100 * 1000,
              method: 'GET',
              responseType: 'blob',
          })
        .catch(function (error) {
            this.setState({ticket_id: undefined})
              console.log(error);
        })
        .then((response) => {
              // response.body.pipeTo(fileStream)

                // console.log(response)

              const url = window.URL.createObjectURL(new Blob([response.data]));
               const link = document.createElement('a');
               link.href = url;
               link.setAttribute('download', 'data.csv'); //or any other extension
               document.body.appendChild(link);
               link.click();


          // const url = window.URL.createObjectURL(new Blob([response.data]));
          // const link = document.createElement('a');
          // link.href = response.data.file;
          // link.setAttribute('download', 'data.csv');
          // document.body.appendChild(link);
          // link.click();
        });
  }

  getQuery(){
      this.setState({app_state : 'Запрос отправлен'});
      let params = this.makeParamsForQuery();

      this.setState({ticked_with_file : this.state.is_file})
      axios.get(
          ''.concat(address_maker('/api/get')), {
              params: params,
              timeout: 60 * 60 * 1000
          })
          .then(this.onTicketRecieved)
          .catch(function (error) {
              console.log(error);
          });
  }


  onFileLoadSelect(){
    this.setState({is_file : !this.state.is_file})
  }

  get_update_date(){
    axios.get(
      ''.concat(address_maker('/api/get_updates_dates'))
    )
      .then((res) => this.onLoadQuery(res))
      .catch(function (error) {
          console.log(error);
      });
    }

  renderLoadTableBlock() {
        if (!this.state.showLoadTable) {
          return null
        }
        console.log(this.state.dateToLoadTable)
        if (this.state.dateToLoadTable === '') {
            console.log(this.state.dateToLoadTable)
            this.setState({ dateToLoadTable : this.props.ask_dict['upd_date'].suggestions[0].value[0]})
        }
       const backTables = [
          {name: 'Компания', value: 'company'},
          // {name: 'Даты жизни', value: 'Alive'},
          {name: 'Налоги', value: 'taxes'},
          // {name: 'ОКВЕД', value: 'OKVED'},
          {name: 'Количество работников', value: 'employee'},
          {name: 'Доход', value: 'income'},
      ]

      return (
          <div style={{ marginRight: '10px', marginLeft: '10px', display: 'flex' }}>

              <div style={{ marginRight: '5px' }}>
                  Выберете таблицу:
                  <select
                      value={ this.state.tableToLoad }
                      onChange={ (event) => {this.setState({ tableToLoad: event.target.value })} }
                  >
                      { backTables.map(item => (
                          <option value={item.value} key={item.value}>
                              { item.name }
                          </option>
                      ))}
                  </select>
              </div>
              <div style={{ marginRight: '5px' }}>
                  Выберете дату:
                  <select
                      value={ this.state.dateToLoadTable }
                      onChange={ event => {
                          console.log(event);
                          this.setState({ dateToLoadTable: String(event.target.value) })
                      } }
                  >
                  {this.props.ask_dict['upd_date'].suggestions.map((item2) => (
                      <option value={item2.value} key={item2.value}>
                          {item2.text}
                      </option>
                  ))}
                  </select>
              </div>

              <button
                  onClick={() => this.loadSingleTable()}
              >
                  Загрузить
              </button>

          </div>
      )
  }

  loadSingleTable() {
      axios(
          ''.concat(address_maker('/api/get/single/')), {
          params: {
              tables: this.state.tableToLoad,
              filter: `upd_date${spase}eq${spase}${this.state.dateToLoadTable}${spase}`,
              file: 'true',
          },
          method: 'GET',
          responseType: 'blob', // important
          timeout: 60 * 60 * 1000
      }).then((response) => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', 'data.csv');
          document.body.appendChild(link);
          link.click();
      })
  }

  render() {
    return (
        <div className="Main">
            <button onClick={() => this.showInfo()}>Справка</button>
            {/*<button onClick={() => this.get_update_date()}>Показать даты обновлений</button>*/}
            <p/>


            <div style={{ display: 'flex' }}>
                <button onClick={() => this.setState({ showLoadTable: !this.state.showLoadTable })}>
                    { !this.state.showLoadTable ? "Выгрузить таблицу" : "Скрыть панель" }
                </button>
                { this.renderLoadTableBlock() }
            </div>

            <div style={{display: 'flex'}}>
                <label>
                    {this.state.app_state}
                </label>
                <ClipLoader
                  // css={override}
                  sizeUnit="px"
                  size={12}
                  color={'#123abc'}
                  loading={this.state.ticket_id !== undefined}
                />
            </div>
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

            {/*{ this.renderExtraFields() }*/}

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
              table_body={this.state.table_body}
          />
        </div>
    );
  }

  renderExtraFields() {
      const backTables = [
          {name: 'Компания', value: 'Company'},
          {name: 'Даты жизни', value: 'Alive'},
          {name: 'Налоги', value: 'TaxBase'},
          // {name: 'ОКВЕД', value: 'OKVED'},
          {name: 'Количество работников', value: 'EmployeeNum'},
          {name: 'Доход', value: 'BaseIncome'},
          // {name: 'Инн', value: 'InnStore'},

      ]
      const display_plus = this.state.extraFields.filter(item => item !== 'del').length === 0
      //const Info = "Используйте этот блок, чтобы добавить таблицы, из которых будут выгружены все возможные поля. " +
      //    "Лучше загружать таблицу ОКВЕД отдельно от всех остальных, так как в них много записей относящихся к одной компании."
      const Info = "Используйте '+' для выбора и загрузки полоной таблицы, удовлетворяющей условиям"
      return (
          <div style={{ marginBottom: '10px' }}>
              <div style={{ marginTop: '5px', marginBottom: '5px', marginRight: '5px' }} >
                  <div style={{ display: 'flex' }}>

                      <div style={{ marginRight: '5px' }}>
                          <button
                              onClick={() => alert(Info)}
                          >
                              ?
                          </button>
                      </div>
                      Выгрузить таблицу
                  </div>
              </div>
              <div style={{ display: 'flex' }}>
                  { this.state.extraFields.map((extraF, index) => {

                      if (extraF === 'del') {
                          return null
                      }

                      return (
                          <div style={{ marginRight: '5px' }}>
                              <button onClick={() => {
                                  const buf = this.state.extraFields
                                  buf[index] = 'del'
                                  this.setState({extraFields: buf})
                              }}>
                                  x
                              </button>
                              <select
                                  value={ this.state.extraFields[index] }
                                  onChange={ val => {
                                      const buf = this.state.extraFields
                                      buf[index] = val.target.value;
                                      this.setState({extraFields: buf})
                                  } }
                              >
                                  { backTables.map(item => (
                                      <option value={ item.value }>
                                          { item.name }
                                      </option>
                                  )) }

                                  {/*<option value={ 'del' }>*/}
                                  {/*    { 'Удалить опцию' }*/}
                                  {/*</option>*/}
                              </select>
                          </div>
                      )
                  })}

                  { display_plus ? (

                      <button onClick={() => this.setState({extraFields : this.state.extraFields.concat(['Company'])})}>
                          +
                      </button>
                    ) : null
                  }
              </div>
          </div>
      )
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
        if (!Array.isArray(this.props.table_human_header)) {
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
                                    row.map((item) =>
                                        (this.render_item(item))
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
            ''.concat(address_maker('/api/ask_dict')), {
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
