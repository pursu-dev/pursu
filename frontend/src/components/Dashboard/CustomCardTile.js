import React, { Component } from 'react';

import { MovableCardWrapper } from 'react-trello/dist/styles/Base';
import DeleteButton from 'react-trello/dist/widgets/DeleteButton';
import moment from 'moment';

const CustomCard = props => {
  const clickDelete = e => {
    props.onDelete();
    e.stopPropagation();
  };
  function isNewPost() {
    let postTime = moment(props.timestamp).unix();
    let lastLogin = moment(props.lastLogin).unix();
    if (postTime > lastLogin) {
      if (props.laneId == 'lane5') {
        if (props.newOffer.flag === false) {
          props.setNewOffer({ offer: true, flag: true });
        }
      }
      return true;
    } else {
      return false;
    }
  }
  let newStyle = props.style;
  if (isNewPost()) {
    newStyle['backgroundColor'] = '#d9f1ff';
  } else {
    newStyle['backgroundColor'] = '#f3f3f3';
  }

  return (
    <MovableCardWrapper
      data-id={props.id}
      onClick={props.onClick}
      style={newStyle}
      className={props.className}
    >
      <header style={{ width: '10vw' }}>
        <div>
          {props.table ? (
            <strong>{props.task}</strong>
          ) : (
            <strong>{props.title}</strong>
          )}
        </div>

        {props.table ? <p>{props.company}</p> : <p></p>}

        {props.showDeleteButton && <DeleteButton onClick={clickDelete} />}
      </header>

      <div>
        <hr style={{ margin: '1em', marginLeft: '0em' }}></hr>
        <div
          style={{
            fontSize: 12,
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {props.table ? <i>{props.deadline}</i> : <i>{props.description}</i>}
        </div>
      </div>
    </MovableCardWrapper>
  );
};

export default CustomCard;
