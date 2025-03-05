import Link from 'next/link'
import Image from 'next/image'
import logoBlackImg from '../../../public/rebalancr_black.webp'

const Footer = () => {
  return (
    <div className="bg-[#8C52FF] text-white mt-32">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center gap-36 py-12">
          <div className="left">
            <div className="flex gap-4 items-center mb-4">
              <Image
                src={logoBlackImg}
                width={60}
                height={45}
                alt="Rebalancer Logo"
              />
              <h2 className="text-[50px] font-medium">Rebalancr</h2>
            </div>
            <p className="text-[24px] font-light leading-[35px] max-w-[454px]">
              Rebalancr is an AI-powered crypto portfolio management tool that
              automates rebalancing to minimize risk and maximize profits
            </p>
          </div>
          <div className="right flex gap-32">
            <div className="box flex flex-col gap-5">
              <h5 className="text-[24px] font-medium">About</h5>
              <Link className="text-[20px] font-light" href="#">
                Manifesto
              </Link>
            </div>
            <div className="box flex flex-col gap-5">
              <h5 className="text-[24px] font-medium">Resources</h5>
              <Link className="text-[20px] font-light" href="#">
                Docs
              </Link>
              <Link className="text-[20px] font-light" href="#">
                Blog
              </Link>
              <Link className="text-[20px] font-light" href="#">
                Github
              </Link>
            </div>
            <div className="box flex flex-col gap-5">
              <h5 className="text-[24px] font-medium">Socials</h5>
              <Link className="text-[20px] font-light" href="#">
                Twitter/X
              </Link>
              <Link className="text-[20px] font-light" href="#">
                Telegram
              </Link>
              <Link className="text-[20px] font-light" href="#">
                Discord
              </Link>
            </div>
          </div>
        </div>
      </div>
      <h6 className="text-[20px] font-medium text-center py-3 border-t border-white">
        Powered by Monad
      </h6>
    </div>
  )
}

export default Footer
