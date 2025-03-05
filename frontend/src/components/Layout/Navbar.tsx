import LogoImg from '../../../public/rebalancr_logo.webp'
import Image from 'next/image'
import { Button } from '../ui/button'
import Link from 'next/link'

const Navbar = () => {
  return (
    <div className="container mx-auto px-4 py-8 flex justify-between items-center">
      <div className="flex gap-2 items-center">
        <Image src={LogoImg} width={60} height={45} alt="Rebalancer Logo" />
        <h1 className="text-[#121212] text-[28px] font-medium">Rebalancr</h1>
      </div>
      <div className="flex gap-8 items-center">
        <Link
          className="text-[20px] font-normal text-[#121212]"
          href="/support"
        >
          Support
        </Link>
        <Button className="rounded-[45px] text-[20px] font-normal text-white bg-[#8C52FF] py-3 px-7 hover:bg-[#8C52FF]/90">
          Connect Wallet
        </Button>
      </div>
    </div>
  )
}

export default Navbar
