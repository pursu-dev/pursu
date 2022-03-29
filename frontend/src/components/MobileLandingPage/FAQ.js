import React, { useState } from 'react';
import { motion } from 'framer-motion';
import styled from 'styled-components';
import tw from 'twin.macro';
import 'styled-components/macro';
import { SectionHeading } from '../misc/Headings.js';
import { Container, ContentWithPaddingXl } from '../misc/Layouts.js';
import { ReactComponent as ChevronDownIcon } from 'feather-icons/dist/icons/chevron-down.svg';
import { ReactComponent as SvgDecoratorBlob1 } from '../../images/svg-decorator-blob-7.svg';
import { ReactComponent as SvgDecoratorBlob2 } from '../../images/svg-decorator-blob-8.svg';

const Heading = tw(SectionHeading)`w-full`;

const Column = tw.div`flex flex-col items-center`;
const HeaderContent = tw.div``;

const FAQSContainer = tw.dl`mt-12 max-w-4xl relative`;
const FAQ = tw.div`cursor-pointer select-none mt-5 px-8 sm:px-10 py-5 sm:py-4 rounded-lg text-gray-800 hover:text-gray-900 bg-gray-200 hover:bg-gray-300 transition duration-300`;
const Question = tw.dt`flex justify-between items-center`;
const QuestionText = tw.span`text-lg lg:text-xl font-semibold`;
const QuestionToggleIcon = motion.custom(styled.span`
  ${tw`ml-2 transition duration-300`}
  svg {
    ${tw`w-6 h-6`}
  }
`);
const Answer = motion.custom(
  tw.dd`pointer-events-none text-sm sm:text-base leading-relaxed`
);

const DecoratorBlob1 = styled(SvgDecoratorBlob1)`
  ${tw`pointer-events-none -z-20 absolute right-0 top-0 h-56 w-56 opacity-15 transform translate-x-2/3 -translate-y-12 text-teal-400`}
`;
const DecoratorBlob2 = styled(SvgDecoratorBlob2)`
  ${tw`pointer-events-none -z-20 absolute left-0 bottom-0 h-64 w-64 opacity-15 transform -translate-x-2/3 text-primary-500`}
`;

export default ({
  heading = 'FAQs',
  faqs = [
    {
      question: 'How much do I have to pay for this service?',
      answer:
        'ZERO. Pursu is completely free of charge for all of its features. We do this to stick closely to our mission of enhancing student productivity during recruiting cycles.',
    },
    {
      question: 'How does this tool work?',
      answer:
        'Pursu scrapes recruiting-related incoming emails and runs the content through our proprietary machine learning algorithms to extract relevant features and automatically update your dashboard.',
    },
    {
      question: 'How is my email data used?',
      answer:
        'TLDR: The data you see on your dashboard is the only data that we store from your emails. The dashboard includes companies, recruiters, stages, and deadlines. If given explicit consent during sign up, we store anonymized emails to improve our prediction models.',
    },
    {
      question: 'What do I do if I have further questions?',
      answer:
        'If you have clarifying questions, we are more than happy to help. Please reach out to hello@pursu.dev.',
    },
  ],
}) => {
  const [activeQuestionIndex, setActiveQuestionIndex] = useState(null);

  const toggleQuestion = questionIndex => {
    if (activeQuestionIndex === questionIndex) setActiveQuestionIndex(null);
    else setActiveQuestionIndex(questionIndex);
  };

  return (
    <Container>
      <ContentWithPaddingXl>
        <Column>
          <HeaderContent>
            <Heading>{heading}</Heading>
          </HeaderContent>
          <FAQSContainer>
            {faqs.map((faq, index) => (
              <FAQ
                key={index}
                onClick={() => {
                  toggleQuestion(index);
                }}
                className="group"
              >
                <Question>
                  <QuestionText>{faq.question}</QuestionText>
                  <QuestionToggleIcon
                    variants={{
                      collapsed: { rotate: 0 },
                      open: { rotate: -180 },
                    }}
                    initial="collapsed"
                    animate={
                      activeQuestionIndex === index ? 'open' : 'collapsed'
                    }
                    transition={{
                      duration: 0.02,
                      ease: [0.04, 0.62, 0.23, 0.98],
                    }}
                  >
                    <ChevronDownIcon />
                  </QuestionToggleIcon>
                </Question>
                <Answer
                  variants={{
                    open: { opacity: 1, height: 'auto', marginTop: '16px' },
                    collapsed: { opacity: 0, height: 0, marginTop: '0px' },
                  }}
                  initial="collapsed"
                  animate={activeQuestionIndex === index ? 'open' : 'collapsed'}
                  transition={{ duration: 0.3, ease: [0.04, 0.62, 0.23, 0.98] }}
                >
                  {faq.answer}
                </Answer>
              </FAQ>
            ))}
          </FAQSContainer>
        </Column>
      </ContentWithPaddingXl>
      <DecoratorBlob1 />
      <DecoratorBlob2 />
    </Container>
  );
};
