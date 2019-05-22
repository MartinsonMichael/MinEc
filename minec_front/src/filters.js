import React, { Component } from 'react';
import './App.css';


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
            sign: this.props.ask_dict[this.state.pos_prop[0]].sign,
            value: "",
        };

    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.handleChangeSign = this.handleChangeSign.bind(this);
    this.handleChangeValue = this.handleChangeValue.bind(this);
    this.validateDate = this.validateDate.bind(this);
    this.validateNumberString = this.validateNumberString.bind(this);
    this.delItem = this.delItem.bind(this);

    this.changeAfterProperty();
    this.handleFilterChange();
  }

  changeAfterProperty(){
      let data = this.state.data;
      if (this.props.ask_dict[data.property].suggestions.length > 0){
        data.value = [].concat(this.props.ask_dict[data.property].suggestions[0]);
      }
      if (this.props.ask_dict[data.property].type === 'date' || this.props.ask_dict[data.property].type === 'number'){
          data.value = "";
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
     let str = event.target.value;
     //str = str.replace(' ', '');
     this.setState({error : 'None'});
     if (!str.match(/^\d{2}\.\d{2}\.\d{4}(-\d{2}\.\d{2}\.\d{4})?(,\d{2}\.\d{2}\.\d{4}(-\d{2}\.\d{2}\.\d{4})?)*$/)){
        this.setState({error :
                "date must be set of a single date 'DD.MM.YYYY' or a " +
                "range DD.MM.YYYY-DD.MM.YYYY, separated by comma without spaces"})
     }

  }

  validateNumberString(event){
     let str = event.target.value;
     //str = str.replace('( )', '');
     this.setState({error : 'None'});
     if (!str.match(/^(\d+(\.\d+)?,|\d+(\.\d+)?-\d+(\.\d+)?,)*(\d+(\.\d+)?|\d+(\.\d+)?-\d+(\.\d+)?)$/)){
         this.setState({error :
                 "number string should consist of numbers and ranges" +
                 " separated by comma, like '12,23-34,234,250-800'"})
     }
  }

  delItem(){
     let data = this.state.data;
     data.property = '---';
     this.setState({data : data});
     this.handleFilterChange();
  }

  render() {
     if (this.state.data.property === '---'){
         return (<a></a>)
     }
    return(
      <div className="row">
          <button onClick={() => this.delItem()}>
              X
          </button>
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
          {this.props.ask_dict[this.state.data.property].sign.map((item) => (
                    <option value={item.value}>
                        {item.name}
                    </option>

            ))}
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
            {this.props.ask_dict[this.state.data.property].type === 'number' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateNumberString}
                />
            ) : (<a></a>)}
            {this.props.ask_dict[this.state.data.property].type === 'date' ? (
                <input
                    type="text"
                    value={this.state.data.value}
                    onChange={this.handleChangeValue}
                    onBlur={this.validateDate}
                />
            ) : (<a></a>)}
        </label>
          {this.state.error === 'None' ? (<a></a>) : (
              <label>
                  {this.state.error}
              </label>

          )}

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
      <div>
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
