import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Autocomplete } from '@material-ui/lab';
import { TextField, Box, Button, Input } from '@material-ui/core';

class NewCardForm extends Component {
  constructor(props) {
    super(props);
    this.state = { desc: '', disabled: true };
    this.createCompanyDropdown = this.createCompanyDropdown.bind(this);
  }

  createCompanyDropdown = query => {
    let lookup = [];
    if (this.props.isDemo) {
      lookup = query.companyList;
      return lookup;
    }

    for (let i = 0; i < query.length; i++) {
      lookup.push(query[i][1]);
    }
    return lookup;
  };

  handleAdd = () => {
    this.props.onAdd({ title: this.titleRef, description: this.state.desc });
  };
  setTitleRef = (e, value) => {
    this.titleRef = value;
    if (
      this.titleRef != null ||
      this.titleRef != '' ||
      this.titleRef != undefined
    ) {
      this.setState({ disabled: false });
    }
  };
  setDescRef = e => {
    this.setState({ desc: e.target.value });
  };

  render() {
    const { onCancel } = this.props;
    let companyLookup = this.createCompanyDropdown(this.props.companies);
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
              <Autocomplete
                id="company"
                freeSolo
                disableClearable
                options={companyLookup.map(company => company)}
                renderInput={params => (
                  <TextField
                    {...params}
                    label="Company"
                    required
                    freeSolo
                    autoFocus={true}
                    margin="normal"
                    variant="outlined"
                  />
                )}
                autoFocus={true}
                name="company"
                onInputChange={this.setTitleRef}
              />
            </div>
            <div style={{ marginBottom: 5 }}>
              <TextField
                variant="outlined"
                margin="normal"
                fullWidth
                id="notes"
                label="Notes"
                name="notes"
                autoComplete="notes"
                value={this.state.desc}
                onChange={this.setDescRef}
              />
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

NewCardForm.propTypes = {
  onCancel: PropTypes.func.isRequired,
  onAdd: PropTypes.func.isRequired,
  t: PropTypes.func.isRequired,
  companies: PropTypes.object,
};

export default NewCardForm;
