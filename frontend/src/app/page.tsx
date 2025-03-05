'use client'

import Navbar from '@/components/Layout/Navbar'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import Image from 'next/image'
import textImg from '../../public/rebalancr_text.webp'
import darkImg from '../../public/dak.webp'
import chatuiImg from '../../public/chat_ui.webp'
import FlowDiagram from '@/components/landing/FlowDiagram'
import Faq from '@/components/landing/Faq'
import Footer from '@/components/Layout/Footer'
import { useAuthRedirect } from '@/hooks/useAuthRedirect'

export default function Home() {
  const { login } = useAuthRedirect()

  return (
    <div className="min-h-screen font-outfit">
      <div className="gradient-bg pb-20">
        <Navbar />

        {/*HERO SECTION*/}
        <div className="grid place-items-center max-w-[716px] mx-auto text-center md:mt-24 mt-12 px-4 md:px-0">
          <h1 className="md:text-[56px] text-[40px] font-medium md:leading-[70px] leading-[50px]">
            Automate Your Portfolio, Maximize Your Gains.
          </h1>
          <p className="text-[24px] font-extralight leading-[30px] mt-3">
            Rebalancr is an AI-powered automated rebalancing protocol designed
            to optimize crypto portfolios. Built on Monad!
          </p>
          <div className="flex gap-8 items-center mt-10">
            <Button
              onClick={login}
              className="rounded-[45px] text-[20px] font-normal text-white bg-[#121212] py-3 px-7 hover:bg-[#121212]/90"
            >
              Connect Wallet
            </Button>
            <Link
              className="hidden md:block text-[20px] font-normal text-[#8C52FF] underline"
              href="/learn-more"
            >
              Learn More
            </Link>
          </div>
        </div>
        <Image
          className="hidden md:block mt-32"
          src={textImg}
          alt="Rebalancr"
        />
      </div>

      {/*FEATURE SECTION*/}
      <div className="container mx-auto px-4 md:mt-40 mt-20">
        <h2 className="md:text-[60px] text-[40px] font-medium text-center md:mb-8 mb-4">
          Features
        </h2>
        <div className="shadow-sm border border-[#D2D2D2] md:pt-10 pt-6 md:pb-12 pb-8 md:px-10 px-8 rounded-[37px] bg-[#8C52FF0D] md:mb-10 mb-7">
          <h4 className="md:text-[40px] text-[28px] font-normal md:mb-8 mb-4">
            AI Powered Optimization
          </h4>
          <p className="md:text-[24px] text-[18px] font-light">
            Rebalancr leverages cutting-edge AI to continuously analyze market
            trends and adjust your portfolio. This data-driven approach ensures
            your assets are always aligned with the most profitable
            opportunities, maximizing returns while minimizing risk.
          </p>
        </div>
        <div className="flex flex-col md:flex-row justify-between items-center md:gap-12 gap-8">
          <div className="shadow-sm border border-[#D2D2D2] md:py-16 md:px-10 py-8 px-8 rounded-[37px] bg-[#8C52FF0D] md:mb-10">
            <h4 className="md:text-[40px] text-[28px] font-normal md:mb-8 mb-4">
              Maximize Yield
            </h4>
            <p className="md:text-[24px] text-[18px] font-light">
              Let Rebalancr optimize your crypto assets, ensuring you’re always
              positioned for the best possible returns, with minimal effort
            </p>
          </div>
          <div className="shadow-sm border border-[#D2D2D2] md:py-16 md:px-10 py-8 px-8 rounded-[37px] bg-[#8C52FF0D] md:mb-10">
            <h4 className="md:text-[40px] text-[28px] font-normal md:mb-8 mb-4">
              Built on Monad
            </h4>
            <p className="md:text-[24px] text-[18px] font-light">
              Rebalancr is leveraging monad 10K TPS in automating swaps with low
              gas fee ensuring maximum yield and preventing loses.
            </p>
          </div>
        </div>
      </div>

      {/*WHAT IS REBALANCR SECTION*/}
      <div className="bg-[#8C52FFFA] mt-20">
        <div className="container mx-auto px-4 text-white">
          <h2 className="md:text-[60px] text-[40px] font-medium md:text-center text-left pt-12 md:mb-12 mb-5">
            What is Rebalancr?
          </h2>
          <div className="flex flex-col-reverse md:flex-row justify-between items-center gap-16 pb-20">
            <Image
              className="flex-1 rounded-[10px]"
              src={darkImg}
              width={578}
              height={750}
              alt="Molandak plugging things"
            />
            <div className="flex-1 flex flex-col gap-4">
              <p className="md:text-[24px] text-[19px] font-light md:leading-[35px] leading-[25px]">
                Rebalancr is an AI-powered automated rebalancing protocol
                designed to optimize crypto portfolios with minimal effort. By
                continuously analyzing market trends and asset performance, it
                intelligently adjusts allocations to minimize risk and maximize
                returns. Whether the market is bullish or bearish, Rebalancr
                ensures your investments stay balanced, so you don’t have to
                constantly monitor or manually trade.
              </p>
              <p className="md:text-[24px] text-[19px] font-light md:leading-[35px] leading-[25px] md:mt-4 mt-1">
                Rebalancr takes the guesswork out of crypto asset management.
                With its seamless automation, security-focused design, and
                data-driven strategies, it helps users protect their wealth
                while maximizing long-term profitability. Stay ahead of the
                market, let AI do the work while you enjoy the gains
              </p>
              <Button
                className="md:mt-8 mt-4 py-3 px-6 w-fit rounded-[30px] md:text-[24px] text-[19px] font-extralight"
                variant="secondary"
              >
                Continue Reading
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/*HOW IT WORKS SECTION*/}
      <div className="mt-24">
        <h2 className="md:text-[60px] text-[40px] font-medium text-center md:mb-16 mb-0">
          How It Works
        </h2>
        <div className="flex justify-between items-center gap-16">
          <div className="flex-1">
            <FlowDiagram />
          </div>
          <Image
            className="flex-2 md:block hidden"
            width={720}
            height={1000}
            src={chatuiImg}
            alt="Chat UI"
          />
        </div>
      </div>

      {/*FAQ SECTION*/}
      <div className="mt-20">
        <h2 className="md:text-[60px] text-[40px] font-medium text-center md:mb-16 mb-10 max-w-[750px] mx-auto">
          Frequently asked questions (FAQ)
        </h2>
        <Faq />
      </div>

      {/*FOOTER SECTION*/}
      <Footer />
    </div>
  )
}
