import React, { Component } from 'react';
import './App.css';

class GroupbyField extends Component{

  constructor(props){
    super(props);
    this.state = {
        error : 'None',
        pos_prop : Object.keys(props.ask_dict),
        data : {
            property: Object.keys(props.ask_dict)[0],
        },
    };
    this.handleChangeProperty = this.handleChangeProperty.bind(this);
    this.delItem = this.delItem.bind(this);

    this.handleGroupbyChange();
  }


    handleChangeProperty(event){
      let data = this.state.data;
      data.property = event.target.value;
      this.setState({data : data});
      this.handleGroupbyChange();
  }

  handleGroupbyChange = () => {
      this.props.onNewData(this.props.index, this.state.data);
  };

  delItem(){
     let data = this.state.data;
     data.property = '---';
     this.setState({data : data});
     this.handleGroupbyChange();
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
              Группировка по :
          </label>

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

export class GroupbyContorll extends Component{
  constructor(props){
    super(props);
    this.state = {
      gb : Array(0),
      data : Array(0),
    };

  }

  addGB(){
    let buf = this.state.gb.slice();
    buf.push(GroupbyField);
    this.setState({gb : buf});
  }


  handleChildChange = (index, pp) => {
      let buf = this.state.data.slice();
      buf[index] = pp;
      this.setState({data : buf});
      this.props.onNewData(1, buf);
  };

  render() {
    return(
      <div style={{ marginTop: '5px' }}>
        {
          this.state.gb.map((component, index) => (
              <div style={{ marginBottom: '5px', marginLeft: '10px' }}>
                  <GroupbyField
                      key={index}
                      index={index}
                      onNewData={this.handleChildChange}
                      ask_dict={this.props.ask_dict}
                  >
                    {component}
                  </GroupbyField>
              </div>
          ))
        }


        <button
            className="add_filter_button"
            onClick={() => this.addGB()}
        >
          Добавить группировку
        </button>
      </div>
    );
  }
}
