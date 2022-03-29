import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Autocomplete } from '@material-ui/lab';
import { TextField } from '@material-ui/core';

function createCompanyDropdown(query) {
  var lookup = [];
  for (let i = 0; i < query.length; i++) {
    lookup.push(query[i][1]);
  }
  return lookup;
}

class NewTodoForm extends Component {
  constructor(props) {
    super(props);
    this.state = { task: '', deadline: '', disabled: true };
  }

  handleAdd = () => {
    let dataToAdd = {
      task: this.state.task,
      deadline: this.state.deadline,
      company: this.companyRef ? this.companyRef : '',
    };
    this.props.onAdd(dataToAdd);
  };
  setTaskRef = (e, value) => {
    this.taskRef = e.target.value;
    if (
      this.taskRef != null ||
      this.taskRef != '' ||
      this.taskRef != undefined
    ) {
      this.setState({ disabled: false });
      this.setState({ task: this.taskRef });
    }
  };
  setDeadlineRef = e => {
    this.setState({ deadline: e.target.value });
  };
  setCompanyRef = (e, value) => {
    this.companyRef = value;
  };

  render() {
    const { onCancel } = this.props;
    let companyLookup = createCompanyDropdown(this.props.companies);
    return (
      <div
        style={{
          background: 'white',
          borderRadius: 3,
          border: '1px solid #eee',
          borderBottom: '1px solid #ccc',
        }}
      >
        <div style={{ padding: 5, margin: 5 }}>
          <div>
            <div style={{ marginBottom: 5 }}>
              <div style={{ marginBottom: 5 }}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  fullWidth
                  required
                  id="task"
                  label="Task"
                  name="task"
                  autoComplete="task"
                  value={this.state.task}
                  onChange={this.setTaskRef}
                />
              </div>
              <div style={{ marginBotton: 5 }}>
                <Autocomplete
                  id="company"
                  freeSolo
                  disableClearable
                  options={companyLookup.map(company => company)}
                  renderInput={params => (
                    <TextField
                      {...params}
                      label="Company"
                      autoFocus={true}
                      margin="normal"
                      variant="outlined"
                    />
                  )}
                  autoFocus={true}
                  name="company"
                  onInputChange={this.setCompanyRef}
                />
              </div>
              <div style={{ marginBotton: 5 }}>
                <TextField
                  variant="outlined"
                  margin="normal"
                  fullWidth
                  type="date"
                  id="deadline"
                  name="deadline"
                  value={this.state.deadline}
                  onChange={this.setDeadlineRef}
                />
              </div>
            </div>
          </div>
          {this.state.disabled ? (
            <button
              style={{ marginRight: 15 }}
              onClick={this.handleAdd}
              disabled
            >
              Add
            </button>
          ) : (
            <button style={{ marginRight: 15 }} onClick={this.handleAdd}>
              Add
            </button>
          )}
          <button onClick={onCancel}>Cancel</button>
        </div>
      </div>
    );
  }
}

NewTodoForm.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired,
  companies: PropTypes.object,
};

export default NewTodoForm;
