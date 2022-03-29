import React from 'react';
import AnimationRevealPage from '../../helpers/AnimationRevealPage.js';
import { Container, ContentWithPaddingXl } from './Layouts';
import tw from 'twin.macro';
import Header from './components/headers/light.js';
import Footer from './components/footers/SimpleFiveColumn.js';
import { SectionHeading } from './Headings';
import styled from 'styled-components';
import 'styled-components/macro';

const HeadingRow = tw.div`flex`;
const Heading = tw(SectionHeading)`text-gray-900 mb-10`;
const Text = styled.div`
  ${tw`text-lg  text-gray-800`}
  p {
    ${tw`mt-2 leading-loose`}
  }
  h1 {
    ${tw`text-3xl font-bold mt-10`}
  }
  h2 {
    ${tw`text-2xl font-bold mt-8`}
  }
  h3 {
    ${tw`text-xl font-bold mt-6`}
  }
  ul {
    ${tw`list-disc list-inside`}
    li {
      ${tw`ml-2 mb-3`}
      p {
        ${tw`mt-0 inline leading-normal`}
      }
    }
  }
`;
export default ({ headingText = 'Privacy Policy' }) => {
  return (
    <AnimationRevealPage>
      <Header />
      <Container>
        <ContentWithPaddingXl>
          <HeadingRow>
            <Heading>{headingText}</Heading>
          </HeadingRow>
          <Text>
            <p>Last updated: June 30, 2020</p>

            <p>
              This Privacy Policy describes Our policies and procedures on the
              collection, use and disclosure of Your information when You use
              the Service and tells You about Your privacy rights and how the
              law protects You.
            </p>

            <p>
              We use Your Personal data to provide and improve the Service. By
              using the Service, You agree to the collection and use of
              information in accordance with this Privacy Policy.
            </p>

            <h1>Who We Are</h1>
            <p>
              Pursu is a productivity enhancement tool designed to help you
              streamline and get the most out of your tech recruiting journey.
            </p>

            <h1>Data We Request</h1>
            <p>
              We collect a variety of information about our users when you
              provide it to us as well as when you use our services. This
              personal data is aggregated and anonymized to ensure our users’
              privacy and security. This data falls into the following
              categories:
            </p>
            <ul>
              <li>
                <p>
                  <strong>Identity data:</strong> This is optional information
                  you provide to us when signing up and includes your
                  university, graduation year, and major.
                </p>
              </li>
              <li>
                <p>
                  <strong>Email data:</strong> Pursu uses email information for
                  the overall benefit of our users. We scrape your emails and
                  run them through a proprietary algorithm to determine which
                  are related to recruiting. We remove any identifying
                  information from these emails and utilize valuable components,
                  including subject line, date, sender, and the email body. This
                  information is used to power your personal recruiting
                  dashboard and the core of our product. If a user gives us
                  explicit consent while signing up, we will remove all
                  identifiable material from the email subject and body, and
                  store this in our database to improve the accuracy of our
                  algorithm moving forward.
                </p>
              </li>
              <li>
                <strong>Usage/Technical Data:</strong> Finally, our product
                contains technologies from third party providers of analytics,
                which helps us compile statistics about our products and
                services and how users engage with them, to ultimately improve
                our offering. We prohibit these analytics providers from
                accessing directly or indirectly identifiable information about
                you.
              </li>
            </ul>

            <h1>Use Cases for Data Collection</h1>
            <p>
              Overall, the data we collect enables us to drive value through our
              product: for example, helping you manage various job applications
              and interview timelines at once, and organizing your recruiting
              process. We may use this data in the following ways:
            </p>
            <ul>
              <li>
                To provide our service to you, carrying out obligations that
                arise from any contracts entered into between you and us
              </li>
              <li>
                To enhance the experience of using our products and services
              </li>
              <li>
                To communicate with you, including sending promotional materials
                and notifications, as well as soliciting feedback on our
                products and services
              </li>
              <li>
                To assemble statistics regarding the use of our products and
                services
              </li>
              <li>To prevent fraud or abuse</li>
              <li>To comply with any legal and/or regulatory obligations</li>
              <li>
                For any other purpose we describe at the time we collect
                information
              </li>
              <li>For any reason you engage us</li>
              <li>For any other purpose with your consent</li>
            </ul>

            <h1>Future Updates</h1>
            <p>
              We may occasionally update this notice. When significant changes
              are made, we will notify users through the Pusu application as
              well as other means, such as email. We encourage users to
              periodically review this notice for the latest information on our
              privacy practices.{' '}
            </p>

            <h1>Contact</h1>
            <p>
              If there are clarifying questions about our privacy policy, we are
              more than happy to help. Please reach out to{' '}
              <a href="mailto:hello@pursu.dev">hello@pursu.dev</a>.
            </p>
          </Text>
        </ContentWithPaddingXl>
      </Container>
      <Footer />
    </AnimationRevealPage>
  );
};
