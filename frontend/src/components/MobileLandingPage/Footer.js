import React from 'react';
import tw from 'twin.macro';
import { Container as ContainerBase } from '../misc/Layouts.js';
import logo from '../../images/Pursu_long_900.png';

const Container = tw(ContainerBase)`relative bg-gray-200 -mx-8 -mb-8`;
const Content = tw.div`max-w-screen-xl mx-auto py-20 lg:py-24`;

const Row = tw.div`flex items-center justify-center flex-col px-8`;

const LogoContainer = tw.div`flex items-center justify-center md:justify-start`;
const LogoImg = tw.img`w-24`;

const CopyrightText = tw.p`text-center mt-10 font-medium tracking-wide text-sm text-gray-600`;
export default () => {
  return (
    <Container>
      <Content>
        <Row>
          <LogoContainer>
            <LogoImg src={logo} />
          </LogoContainer>

          <CopyrightText>
            &copy; Copyright 2022, Pursu. All Rights Reserved.
          </CopyrightText>
        </Row>
      </Content>
    </Container>
  );
};
