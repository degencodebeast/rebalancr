'use client'

import LogoImg from '../../../public/rebalancr_logo.webp'
import Image from 'next/image'
import { Button } from '../ui/button'
import Link from 'next/link'
import { Burger } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { useAuthRedirect } from '@/hooks/useAuthRedirect'

const Navbar = () => {
  const [opened, { toggle }] = useDisclosure()
  const { login } = useAuthRedirect()

  return (
    <nav className="container mx-auto px-4 py-8">
      {/* Desktop & Mobile Header */}
      <div className="flex justify-between items-center">
        <div className="flex gap-2 items-center">
          <Image src={LogoImg} width={60} height={45} alt="Rebalancer Logo" />
          <h1 className="text-[#121212] text-[28px] font-medium">Rebalancr</h1>
        </div>

        {/* Desktop Navigation */}
        <div className="hidden md:flex gap-8 items-center">
          <Link
            className="text-[20px] font-normal text-[#121212]"
            href="/support"
          >
            Support
          </Link>
          <Button
            onClick={login}
            className="rounded-[45px] text-[20px] font-normal text-white bg-[#8C52FF] py-3 px-7 hover:bg-[#8C52FF]/90"
          >
            Connect Wallet
          </Button>
        </div>

        {/* Mobile Burger Button */}
        <Burger
          className="md:hidden p-2"
          opened={opened}
          onClick={toggle}
          aria-label="Toggle navigation"
          size="md"
          color="#121212"
        />
      </div>

      {/* Mobile Navigation */}
      <div
        className={`md:hidden transition-all duration-300 ease-in-out ${
          opened
            ? 'max-h-64 opacity-100 visible mt-4'
            : 'max-h-0 opacity-0 invisible'
        }`}
      >
        <div className="flex flex-col gap-4 py-4">
          <Button
            onClick={login}
            className="rounded-[45px] text-[20px] font-normal text-white bg-[#8C52FF] py-3 px-7 hover:bg-[#8C52FF]/90 w-full"
          >
            Connect Wallet
          </Button>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
