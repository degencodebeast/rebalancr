'use client'

import { AppShell, Avatar, Burger, NavLink } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { usePathname, useRouter } from 'next/navigation'
import { usePrivy } from '@privy-io/react-auth'
import DashboardIcon from '../icons/DashboardIcon'
import AssetsIcon from '../icons/AssetsIcon'
import AnalyticsIcon from '../icons/AnalyticsIcon'
import HistoryIcon from '../icons/HistoryIcon'
import SettingsIcon from '../icons/SettingsIcon'
import SupportIcon from '../icons/SupportIcon'
import { useEffect } from 'react'
import { Button } from '../ui/button'
import LogoImg from '../../../public/rebalancr_logo.webp'
import sidenavImg from '../../../public/sidenav_img.webp'
import Image from 'next/image'
import { blo } from 'blo'
import '@/components/Layout/dashboard.scss'

// Define navigation links
const navLinks = [
  {
    icon: <DashboardIcon />,
    name: 'Dashboard',
    url: '/dashboard',
  },
  {
    icon: <AssetsIcon />,
    name: 'Assets',
    url: '/assets',
  },
  {
    icon: <AnalyticsIcon />,
    name: 'Analytics',
    url: '/analytics',
  },
  {
    icon: <HistoryIcon />,
    name: 'History',
    url: '/history',
  },
  {
    icon: <SettingsIcon />,
    name: 'Settings',
    url: '/settings',
  },
  {
    icon: <SupportIcon />,
    name: 'Support',
    url: '/support',
  },
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [opened, { toggle }] = useDisclosure()
  const pathname = usePathname()
  const router = useRouter()
  const { authenticated, ready, logout, user } = usePrivy()

  // Redirect to home if not authenticated
  useEffect(() => {
    if (ready && !authenticated) {
      router.push('/')
    }
  }, [ready, authenticated, router])

  // If not authenticated, don't render the dashboard
  if (!authenticated) {
    return null
  }

  return (
    <AppShell
      layout="alt"
      header={{ height: 90 }}
      navbar={{
        width: 350,
        breakpoint: 'md',
        collapsed: { mobile: !opened },
      }}
      withBorder={false}
    >
      <AppShell.Header>
        <div className="flex items-center gap-6">
          <Burger
            opened={opened}
            onClick={toggle}
            hiddenFrom="md"
            size="md"
            color="white"
          />
          <div className="flex items-center gap-3">
            <Avatar
              className="border border-white"
              radius="xl"
              src={blo(`0x${user?.wallet?.address}`)}
            />
            <div className="logo text-white text-xl">Nad Keone</div>
          </div>
        </div>
        <Button variant="outline" onClick={logout}>
          Sign Out
        </Button>
      </AppShell.Header>

      <AppShell.Navbar className="sidenav_wrapper relative">
        <div className="mb-12  mt-8 flex justify-between items-center">
          <div className="flex gap-4 items-center">
            <Image src={LogoImg} width={60} height={45} alt="Rebalancer Logo" />
            <h1 className="text-[#f0f0f0] text-[32px] font-medium">
              Rebalancr
            </h1>
          </div>
          <Burger
            opened={opened}
            onClick={toggle}
            hiddenFrom="md"
            size="md"
            color="white"
          />
        </div>
        {navLinks.map((link, index) => (
          <NavLink
            className="rounded-[10px] py-2"
            key={index}
            active={pathname.startsWith(link.url)}
            label={link.name}
            leftSection={link.icon}
            onClick={() => router.push(link.url)}
          />
        ))}
        <Image
          className="sidenav_img absolute w-full bottom-0 left-0"
          src={sidenavImg}
          alt="sidenav image"
        />
      </AppShell.Navbar>

      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  )
}
