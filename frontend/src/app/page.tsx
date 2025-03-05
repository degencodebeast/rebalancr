'use client'

import Navbar from '@/components/Layout/Navbar'
import { Button } from '@/components/ui/button'
import { useLogin, usePrivy } from '@privy-io/react-auth'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import textImg from '../../public/rebalancr_text.webp'
import darkImg from '../../public/dak.webp'
import chatuiImg from '../../public/chat_ui.webp'
import Image from 'next/image'
import FlowDiagram from '@/components/landing/FlowDiagram'
import Faq from '@/components/landing/Faq'
import Footer from '@/components/Layout/Footer'

export default function Home() {
  const router = useRouter()
  const { authenticated, ready } = usePrivy()

  // Check if user is already authenticated and redirect
  useEffect(() => {
    if (ready && authenticated) {
      router.push('/dashboard')
    }
  }, [ready, authenticated, router])

  const { login } = useLogin({
    onComplete: async ({}) => {
      // Redirect to dashboard after successful login
      router.push('/dashboard')
    },
  })

  return (
    <div className="min-h-screen font-outfit">
      <div className="gradient-bg pb-20">
        <Navbar />

        {/*HERO SECTION*/}
        <div className="grid place-items-center max-w-[716px] mx-auto text-center mt-24">
          <h1 className="text-[56px] font-medium leading-[70px]">
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
              className="text-[20px] font-normal text-[#8C52FF] underline"
              href="/learn-more"
            >
              Learn More
            </Link>
          </div>
        </div>
        <Image className="mt-32" src={textImg} alt="Rebalancr" />
      </div>

      {/*FEATURE SECTION*/}
      <div className="container mx-auto px-4 mt-40">
        <h2 className="text-[60px] font-medium text-center mb-8">Features</h2>
        <div className="shadow-sm border border-[#D2D2D2] pt-10 pb-12 px-10 rounded-[37px] bg-[#8C52FF0D] mb-10">
          <h4 className="text-[40px] font-normal mb-8">
            AI Powered Optimization
          </h4>
          <p className="text-[24px] font-light">
            Rebalancr leverages cutting-edge AI to continuously analyze market
            trends and adjust your portfolio. This data-driven approach ensures
            your assets are always aligned with the most profitable
            opportunities, maximizing returns while minimizing risk.
          </p>
        </div>
        <div className="flex justify-between items-center gap-12">
          <div className="shadow-sm border border-[#D2D2D2] py-16 px-10 rounded-[37px] bg-[#8C52FF0D] mb-10">
            <h4 className="text-[40px] font-normal mb-8">Maximize Yield</h4>
            <p className="text-[24px] font-light">
              Let Rebalancr optimize your crypto assets, ensuring you’re always
              positioned for the best possible returns, with minimal effort
            </p>
          </div>
          <div className="shadow-sm border border-[#D2D2D2] py-16 px-10 rounded-[37px] bg-[#8C52FF0D] mb-10">
            <h4 className="text-[40px] font-normal mb-8">Built on Monad</h4>
            <p className="text-[24px] font-light">
              Rebalancr is leveraging monad 10K TPS in automating swaps with low
              gas fee ensuring maximum yield and preventing loses.
            </p>
          </div>
        </div>
      </div>

      {/*WHAT IS REBALANCR SECTION*/}
      <div className="bg-[#8C52FFFA] mt-20">
        <div className="container mx-auto px-4 text-white">
          <h2 className="text-[60px] font-medium text-center pt-12 mb-12">
            What is Rebalancr?
          </h2>
          <div className="flex justify-between items-center gap-16 pb-20">
            <Image
              className="flex-1 rounded-[10px]"
              src={darkImg}
              width={578}
              height={750}
              alt="Molandak plugging things"
            />
            <div className="flex-1 flex flex-col gap-4">
              <p className="text-[24px] font-light leading-[35px]">
                Rebalancr is an AI-powered automated rebalancing protocol
                designed to optimize crypto portfolios with minimal effort. By
                continuously analyzing market trends and asset performance, it
                intelligently adjusts allocations to minimize risk and maximize
                returns. Whether the market is bullish or bearish, Rebalancr
                ensures your investments stay balanced, so you don’t have to
                constantly monitor or manually trade.
              </p>
              <p className="text-[24px] font-light leading-[35px] mt-4">
                Rebalancr takes the guesswork out of crypto asset management.
                With its seamless automation, security-focused design, and
                data-driven strategies, it helps users protect their wealth
                while maximizing long-term profitability. Stay ahead of the
                market, let AI do the work while you enjoy the gains
              </p>
              <Button
                className="mt-8 py-3 px-6 w-fit rounded-[30px] text-[24px] font-extralight"
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
        <h2 className="text-[60px] font-medium text-center mb-16">
          How It Works
        </h2>
        <div className="flex justify-between items-center gap-16">
          <div className="flex-1">
            <FlowDiagram />
          </div>
          <Image
            className="flex-2"
            width={720}
            height={1000}
            src={chatuiImg}
            alt="Chat UI"
          />
        </div>
      </div>

      {/*FAQ SECTION*/}
      <div className="mt-20">
        <h2 className="text-[60px] font-medium text-center mb-16 max-w-[750px] mx-auto">
          Frequently asked questions (FAQ)
        </h2>
        <div className="">
          <Faq />
        </div>
      </div>

      {/*FOOTER SECTION*/}
      <Footer />
    </div>
  )
}
