import React from 'react';
import Switch from '@material-ui/core/Switch';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';

export default function TableSwitch(props) {
  return (
    <FormControl component="fieldset">
      <FormGroup aria-label="position" row>
        <FormControlLabel
          value="table"
          control={
            <Switch
              checked={props.checked}
              onChange={props.onChange}
              color="primary"
            />
          }
          // label="Table Position"
          // labelPlacement="end"
        />
      </FormGroup>
    </FormControl>
  );
}
