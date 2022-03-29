import React from 'react';
import ToolbarComponent from '../Shared/Toolbar';
import HamburgerDrawer from './HamburgerDrawer';

export default function Navbar(props) {
  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <div>
      <ToolbarComponent
        openDrawer={handleDrawerOpen}
        openSettings={props.openSettings}
        data={props.data}
        handleCompanyModalOpen={props.handleCompanyModalOpen}
        handleCompanyModalClose={props.handleCompanyModalClose}
        email={props.email}
        page={props.page}
        filter={props.filter}
        pipelines={props.pipelines}
        isDemo={props.isDemo}
      />
      <HamburgerDrawer
        open={open}
        onClose={handleDrawerClose}
        email={props.email}
      />
    </div>
  );
}
