'use client'

import DashboardLayout from '@/components/Layout/DashboardLayout'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import btcIcon from '../../../public/btc.svg'
import ethIcon from '../../../public/eth.svg'
import usdtIcon from '../../../public/usdt.svg'

export default function Assets() {
  return (
    <DashboardLayout>
      <div className="p-8">
        <div className="mb-6">
          <h1 className="text-[40px] font-medium">Your Assets</h1>
          <h2 className="text-[64px] font-medium">$10,000</h2>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-12">
          <Button className="bg-[#8C52FF] text-white rounded-full px-12 py-6 text-[24px] font-normal hover:bg-[#8C52FF]/90">
            Send
          </Button>
          <Button
            variant="outline"
            className="bg-white text-black rounded-full px-12 py-6 text-[24px] font-normal border-2 hover:bg-gray-50"
          >
            Receive
          </Button>
        </div>

        {/* Asset Cards */}
        <div className="grid grid-cols-2 gap-6">
          {/* Bitcoin Card */}
          <div className="bg-[#8C52FF] rounded-[20px] p-6 gap-3 flex flex-col items-start">
            <div className="flex items-center gap-4 flex-1">
              <Image src={btcIcon} alt="Bitcoin" width={40} height={40} />
              <span className="text-[24px] text-white">Bitcoin</span>
            </div>
            <span className="text-[40px] text-white">0.05 BTC</span>
          </div>

          {/* Ethereum Card */}
          <div className="bg-[#121212] rounded-[20px] p-6 gap-3 flex flex-col items-start">
            <div className="flex items-center gap-4 flex-1">
              <Image src={ethIcon} alt="Ethereum" width={40} height={40} />
              <span className="text-[24px] text-white">Ethereum</span>
            </div>
            <span className="text-[40px] text-white">0.5 ETH</span>
          </div>

          {/* USDT Card */}
          <div className="bg-[#121212] rounded-[20px] p-6 gap-3 flex flex-col items-start">
            <div className="flex items-center gap-4 flex-1">
              <Image src={usdtIcon} alt="Tether USDT" width={40} height={40} />
              <span className="text-[24px] text-white">Tether USDT</span>
            </div>
            <span className="text-[40px] text-white">$1,500</span>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
