import React from 'react';
import styled from 'styled-components';
import tw from 'twin.macro';
import {
  SectionHeading,
  Subheading as SubheadingBase,
} from '../misc/Headings.js';
import { SectionDescription } from '../misc/Typography.js';
import MailIconImage from '../../images/mail-outline.svg';
import OptionsIconImage from '../../images/options-icon.svg';
import CheckIconImage from '../../images/checkmark-icon.svg';

const Container = tw.div`relative bg-primary-900 -mx-8 px-8 text-gray-100`;
const ThreeColumnContainer = styled.div`
  ${tw`flex flex-col items-center md:items-stretch md:flex-row flex-wrap md:justify-center max-w-screen-lg mx-auto py-20 md:py-24`}
`;
const Subheading = tw(SubheadingBase)`mb-4 text-gray-100`;
const Heading = tw(SectionHeading)`w-full`;
const Description = tw(SectionDescription)`w-full text-center text-gray-300`;
const VerticalSpacer = tw.div`mt-10 w-full`;
const Column = styled.div`
  ${tw`md:w-1/2 lg:w-1/3 max-w-xs`}
`;
const Card = styled.div`
  ${tw`flex flex-col items-center text-center h-full mx-4 px-2 py-8`}
  .imageContainer {
    ${tw`bg-gray-100 text-center rounded-full p-5 flex-shrink-0`}
    img {
      ${tw`w-6 h-6`}
    }
  }
  .textContainer {
    ${tw`mt-6`}
  }
  .title {
    ${tw`text-gray-400 tracking-wider font-bold text-xl leading-none`}
  }
  .description {
    ${tw`mt-2 font-normal text-gray-400 leading-snug`}
  }
`;
export default ({
  cards = null,
  heading = 'Features',
  subheading = '',
  description = 'Learn about how Pursu can help you.',
}) => {
  /*
   * This componets has an array of object denoting the cards defined below. Each object in the cards array can have the key (Change it according to your need, you can also add more objects to have more cards in this feature component) or you can directly pass this using the cards prop:
   *  1) imageSrc - the image shown at the top of the card
   *  2) title - the title of the card
   *  3) description - the description of the card
   *  If a key for a particular card is not provided, a default value is used
   */
  const defaultCards = [
    {
      imageSrc: MailIconImage,
      title: 'Minimal User Input',
      description:
        'Say goodbye to manually updating your spreadsheet. Pursu automatically processes recruiting-relevant emails and updates your dashboard.',
    },
    {
      imageSrc: OptionsIconImage,
      title: 'Customized Insights',
      description:
        "Your personal dashboard gives you a bird's eye view of your recruiting progress and deadlines with different companies.",
    },
    {
      imageSrc: CheckIconImage,
      title: 'Managed Tasks',
      description:
        'A to-do list is automatically generated with relevant action items to keep you focused and productive.',
    },
  ];
  if (!cards) cards = defaultCards;
  return (
    <Container>
      <ThreeColumnContainer>
        {subheading && <Subheading>{subheading}</Subheading>}
        <Heading>{heading}</Heading>
        {description && <Description>{description}</Description>}
        <VerticalSpacer />
        {cards.map((card, i) => (
          <Column key={i}>
            <Card>
              <span className="imageContainer">
                <img src={card.imageSrc} alt="" />
              </span>
              <span className="textContainer">
                <span className="title">{card.title}</span>
                <p className="description">{card.description}</p>
              </span>
            </Card>
          </Column>
        ))}
      </ThreeColumnContainer>
    </Container>
  );
};
