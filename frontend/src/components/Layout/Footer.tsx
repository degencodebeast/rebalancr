import Link from 'next/link'
import Image from 'next/image'
import logoBlackImg from '../../../public/rebalancr_black.webp'
import monadLogoImg from '../../../public/monad_logo.png'

const Footer = () => {
  return (
    <div className="bg-[#8C52FF] text-white mt-32">
      <div className="container mx-auto px-4">
        <div className="flex md:flex-row flex-col justify-between md:items-center items-start md:gap-36 gap-12 py-12">
          <div className="left">
            <div className="flex gap-4 items-center mb-4">
              <Image
                src={logoBlackImg}
                width={60}
                height={45}
                alt="Rebalancer Logo"
              />
              <h2 className="md:text-[50px] text-[40px] font-medium">
                Rebalancr
              </h2>
            </div>
            <p className="md:text-[24px] text-[22px] font-light md:leading-[35px] leading-[30px] max-w-[454px]">
              Rebalancr is an AI-powered crypto portfolio management tool that
              automates rebalancing to minimize risk and maximize profits
            </p>
          </div>
          <div className="right flex flex-wrap md:flex-nowrap md:gap-32 gap-10">
            <div className="box flex flex-col md:gap-5 gap-2">
              <h5 className="md:text-[24px] text-[22px] font-medium">About</h5>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Manifesto
              </Link>
            </div>
            <div className="box flex flex-col md:gap-5 gap-2">
              <h5 className="md:text-[24px] text-[22px] font-medium">
                Resources
              </h5>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Docs
              </Link>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Blog
              </Link>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Github
              </Link>
            </div>
            <div className="box flex flex-col md:gap-5 gap-2">
              <h5 className="md:text-[24px] text-[22px] font-medium">
                Socials
              </h5>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Twitter/X
              </Link>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Telegram
              </Link>
              <Link className="md:text-[20px] text-[18px] font-light" href="#">
                Discord
              </Link>
            </div>
          </div>
        </div>
      </div>
      <div className="flex items-center justify-center gap-2 border-t border-white">
        <h6 className="md:text-[20px] text-[18px] font-medium text-center py-3">
          Powered by Monad
        </h6>
        <Image src={monadLogoImg} width={32} height={32} alt="Monad Logo" />
      </div>
    </div>
  )
}

export default Footer
