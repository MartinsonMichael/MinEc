import React, { Component } from 'react';
import './App.css';
import Popup from "reactjs-popup";


const ReactTags = require('react-tag-autocomplete');

class FilterField extends Component{

  constructor(props){
    super(props);
    this.state = {
        pos_prop : Object.keys(props.ask_dict),
        data : 0,
        error : 'None',
        info: false,
    };
    this.state.data = {
            property: this.state.pos_prop[0],
            sign: this.props.ask_dict[this.state.pos_prop[0]].sign,
            value: "",
        };

    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.handleChangeSign = this.handleChangeSign.bind(this);
    this.handleChangeValue = this.handleChangeValue.bind(this);
    this.validateDate = this.validateDate.bind(this);
    this.validateNumberString = this.validateNumberString.bind(this);
    this.delItem = this.delItem.bind(this);
    this.showInfo = this.showInfo.bind(this);
    this.showInfo = this.showInfo.bind(this);
    this.render_multi = this.render_multi.bind(this);
    this.handleValueArrayAdd = this.handleValueArrayAdd.bind(this);
    this.handleValueArrayChange = this.handleValueArrayChange.bind(this);

    this.changeAfterProperty();
    this.handleFilterChange();
  }

  changeAfterProperty(){
      let data = this.state.data;
      if (this.props.ask_dict[data.property].suggestions.length > 0){
        data.value = [].concat(this.props.ask_dict[data.property].suggestions[0].value);
      }
      if (this.props.ask_dict[data.property].type === 'date' || this.props.ask_dict[data.property].type === 'number'){
          data.value = "";
      }
      if (this.props.ask_dict[data.property].type === 'bool'){
          data.value = "True";
      }
      data.sign = this.props.ask_dict[this.state.data.property].sign[0].value;
      this.setState({data : data});
  }

  handleChangeProperty(event){
      let data = this.state.data;
      data.property = event.target.value;
      this.setState({data : data});
      this.changeAfterProperty();
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

 // handleDelete (i) {
 //    let data = this.state.data;
 //    data.value = data.value.slice(0);
 //    data.value.splice(i, 1);
 //    this.setState({ data : data })
 //  }

  handleValueArrayChange = (index) => (event) => {
    let data = this.state.data;
    data.value[index] = event.target.value;
    this.setState({ data : data });
      this.handleFilterChange()
  };

  handleValueArrayAdd(){
    let data = this.state.data;
    data.value = data.value.concat([this.props.ask_dict[data.property].suggestions[0]].value);
    this.setState({ data : data })
  }

  validateDate(event){
     let str = event.target.value;
     //str = str.replace(' ', '');
     this.setState({error : 'None'});
     if (!str.match(/^\d{2}\.\d{2}\.\d{4}(-\d{2}\.\d{2}\.\d{4})?(,\d{2}\.\d{2}\.\d{4}(-\d{2}\.\d{2}\.\d{4})?)*$/)){
         const description = this.props.ask_dict[this.state.data.property].description;
         alert('Неправильный формат данных!\n\n' + description.type_description)
        // this.setState({error :
        //         "date must be set of a single date 'DD.MM.YYYY' or a " +
        //         "range DD.MM.YYYY-DD.MM.YYYY, separated by comma without spaces"})
     }

  }

  validateNumberString(event){
     let str = event.target.value;
     //str = str.replace('( )', '');
     this.setState({error : 'None'});
     if (!str.match(/^(\d+(\.\d+)?,|\d+(\.\d+)?-\d+(\.\d+)?,)*(\d+(\.\d+)?|\d+(\.\d+)?-\d+(\.\d+)?)$/)){
         const description = this.props.ask_dict[this.state.data.property].description;
         alert('Неправильный формат данных!\n\n' + description.type_description)
         // this.setState({error :
         //         "number string should consist of numbers and ranges" +
         //         " separated by comma, like '12,23-34,234,250-800'"})
     }
  }

  delItem(){
     let data = this.state.data;
     data.property = '---';
     this.setState({data : data});
     this.handleFilterChange();
  }

  showInfo() {
    this.setState({info: !this.state.info})
  }

  render_info() {
    const description = this.props.ask_dict[this.state.data.property].description;
    alert(description.name_description + '\n\n' + description.type_description)
     // return (
     //     <React.Fragment>
     //         <Dialog open={true}>
     //             <h1>{this.state.data.property}</h1>
     //             <div>
     //                 {description.name_description}
     //                 {description.type_description}
     //             </div>
     //             <button onClick={this.showInfo()}>
     //                 Ok
     //             </button>
     //         </Dialog>
     //     </React.Fragment>
     // )
  }

  render_multi(){
      return (
        <div>
            {this.state.data.value.map((item, i) => (
                <select
                    value={item}
                    onChange={this.handleValueArrayChange(i)}
                >
                    {this.props.ask_dict[this.state.data.property].suggestions.map((item2) => (
                    <option value={item2.value}>
                        {item2.text}
                    </option>

                    ))}
                </select>
            ))}
            <button onClick={this.handleValueArrayAdd}>+</button>
        </div>
      )
  }

  render() {
     if (this.state.data.property === '---'){
         return null
     }
     //const description = this.props.ask_dict[this.state.data.property].description;
      const property_type = this.props.ask_dict[this.state.data.property].type;
     return(
      <div className="row">
          <button onClick={() => this.delItem()}>
              X
          </button>
          <button onClick={() => this.render_info()}>
              ?
          </button>
          {/*<Popup position="top left">*/}
          {/*  {close => (*/}
          {/*    <div>*/}
          {/*        {description.name_description}*/}
          {/*        {description.type_description}*/}
          {/*      <a className="close" onClick={close}>*/}
          {/*        &times;*/}
          {/*      </a>*/}
          {/*    </div>*/}
          {/*  )}*/}
          {/*</Popup>*/}
        <select
            value={this.state.data.property}
            onSelect={this.handleChangeProperty}
            onChange={this.handleChangeProperty}
        >
            {this.state.pos_prop.map((item) => (
                    <option value={item}>
                        {this.props.ask_dict[item].human_name}
                    </option>

            ))}
        </select>
        <select
            value={this.state.data.sign}
            onSelect={this.handleChangeSign}
            onChange={this.handleChangeSign}
        >
          {this.props.ask_dict[this.state.data.property].sign.map((item) => (
                    <option value={item.value}>
                        {item.name}
                    </option>

            ))}
        </select>
        <label>
            {property_type === 'bool' ? (
                <select
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                >
                    <option value={"True"}> Да </option>
                    <option value={"False"}> Нет </option>
                </select>
            ) : null}
            {property_type === 'multi' ? (
                this.render_multi()
            ) : null}
            {property_type === 'number' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateNumberString}
                />
            ) : null}
            {property_type === 'date' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateDate}
                />
            ) : null}
        </label>

      </div>
    );

  }
}

export class FilterController extends Component{
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
      <div style={{ marginTop: '5px' }}>
        {
          this.state.filters.map((component, index) => (
              <div style={{ marginBottom: '5px', marginLeft: '10px' }}>
                  <FilterField
                      key={index}
                      index={index}
                      onNewData={this.handleChildChange}
                      ask_dict={this.props.ask_dict}
                  >
                    {component}
                  </FilterField>
              </div>
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
