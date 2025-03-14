'use client'

import { Accordion } from '@mantine/core'
import PlusIcon from '../icons/PlusIcon'

const Faq = () => {
  const faqData = [
    {
      question: 'What is rebalancr and what problem does it solve?',
      answer: `Rebalancr is an AI-powered portfolio management protocol that automatically rebalances your crypto assets to maintain optimal allocation. It solves the challenge of manual portfolio management by using advanced algorithms to maximize returns while minimizing risks in both bull and bear markets.`,
    },
    {
      question: 'Why build on Monad and not other chains?',
      answer: `We chose Monad for its superior performance with 10,000 TPS and minimal gas fees. This high throughput and cost-efficiency are crucial for frequent portfolio rebalancing operations, ensuring our users get the best possible returns without excessive transaction costs.`,
    },
    {
      question: 'How secure are my assets with rebalancr?',
      answer: `Your assets remain secure through our non-custodial approach - we never hold your funds directly. Smart contracts are audited by leading security firms, and all operations are transparent on the blockchain. We implement multiple security layers to protect your investments.`,
    },
  ]

  return (
    <div className="container mx-auto px-4">
      <Accordion
        variant="filled"
        radius="md"
        className="max-w-[1000px] mx-auto"
        chevron={<PlusIcon />}
        classNames={{
          chevron: 'text-[#8C52FF]',
        }}
        styles={{
          chevron: {
            width: '24px',
            height: '24px',
          },
        }}
      >
        {faqData.map((faq, index) => (
          <Accordion.Item
            key={index}
            value={`item-${index}`}
            className="mb-6 overflow-hidden bg-[#8C52FF0D] md:p-5 px-0 hover:border-[#8C52FF] hover:border transition-all"
            styles={{
              item: {
                borderRadius: '20px',
              },
            }}
          >
            <Accordion.Control className="hover:bg-transparent md:py-6 py-4 px-8">
              <span className="md:text-[24px] text-[20px] font-normal">
                {faq.question}
              </span>
            </Accordion.Control>
            <Accordion.Panel className="md:py-4 py-2 md:px-8 px-4">
              <p className="md:text-[20px] text-[18px] font-light leading-[30px]">
                {faq.answer}
              </p>
            </Accordion.Panel>
          </Accordion.Item>
        ))}
      </Accordion>
    </div>
  )
}

export default Faq
