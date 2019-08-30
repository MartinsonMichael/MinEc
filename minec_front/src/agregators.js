import React, { Component } from 'react';
import './App.css';


const ReactTags = require('react-tag-autocomplete');

class AggField extends Component{

  constructor(props){
    super(props);
    this.state = {
        error : 'None',
        pos_prop : Object.keys(props.ask_dict),
        data : {
            sign: "sum",
            property: Object.keys(props.ask_dict)[0],
        },
    };

    this.handleChangeSign = this.handleChangeSign.bind(this);
    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.delItem = this.delItem.bind(this);

    this.handleAggChange();
  }

    handleChangeSign(event){
      let data = this.state.data;
      data.sign = event.target.value;
      this.setState({data : data});
      this.handleAggChange();
  }

    handleChangeProperty(event){
      let data = this.state.data;
      data.property = event.target.value;
      this.setState({data : data});
      this.handleAggChange();
  }

  handleAggChange = () => {
      this.props.onNewData(this.props.index, this.state.data);
  };

  //
  //  handleDelete (i) {
  //   let data = this.state.data;
  //   data.property.splice(i, 1);
  //   this.setState({ data : data });
  //   this.handleAggChange();
  // }
  //
  // handleAddition (tag) {
  //   let data = this.state.data;
  //   data.property = [].concat(data.property, tag);
  //   this.setState({ data : data });
  //   this.handleAggChange();
  // }

    delItem(){
     let data = this.state.data;
     data.property = '---';
     this.setState({data : data});
     this.handleAggChange();
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
          <label>
              Тип агрегации
          </label>
          <select
            value={this.state.data.sign}
            onSelect={this.handleChangeSign}
            onChange={this.handleChangeSign}
          >
            <option value="sum"> Сумма </option>
            <option value="count"> Количество </option>
            <option value="avg"> Среднее арифметическое </option>
          </select>

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


      </div>
    );

  }
}

export class AgregatorContorll extends Component{
  constructor(props){
    super(props);
    this.state = {
      agg : Array(0),
      data : Array(0),
    };

  }

  addAgg(){
    let buf = this.state.agg.slice();
    buf.push(AggField);
    this.setState({agg : buf});
  }


  handleChildChange = (index, pp) => {
      let buf = this.state.data.slice();
      buf[index] = pp;
      this.setState({data : buf});
      this.props.onNewData(2, buf);
  };

  render() {
    return(
      <div style={{ marginTop: '5px' }}>
        {
          this.state.agg.map((component, index) => (
              <div style={{ marginBottom: '5px', marginLeft: '10px' }}>
                  <AggField
                      key={index}
                      index={index}
                      onNewData={this.handleChildChange}
                      ask_dict={this.props.ask_dict}
                  >
                    {component}
                  </AggField>
              </div>
          ))
        }


        <button onClick={() => this.addAgg()}>
          Добавить агрегатор
        </button>
      </div>
    );
  }
}
