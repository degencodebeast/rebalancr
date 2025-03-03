'use client'

import { AppShell, Burger, Group, NavLink } from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { NavLinks } from './interface'
import { usePathname, useRouter } from 'next/navigation'
import DashboardIcon from '../icons/DashboardIcon'
import AssetsIcon from '../icons/AssetsIcon'
import AnalyticsIcon from '../icons/AnalyticsIcon'
import HistoryIcon from '../icons/HistoryIcon'
import SettingsIcon from '../icons/SettingsIcon'
import SupportIcon from '../icons/SupportIcon'
import Image from 'next/image'

const navLinks: NavLinks[] = [
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

export default function ParentWrapper({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const [opened, { toggle }] = useDisclosure()
  const router = useRouter()
  const pathname = usePathname()

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 250, breakpoint: 'sm', collapsed: { mobile: !opened } }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Image src="/rebalancer_logo.png" alt="Rebalancer Logo" />
        </Group>
      </AppShell.Header>
      <AppShell.Navbar p="md" className="sidenav_wrapper">
        {navLinks.map((link, index) => (
          <NavLink
            className="rounded-[10px] py-2 text-black"
            key={index}
            active={pathname.startsWith(link.url!)}
            label={link.name}
            leftSection={link.icon}
            onClick={() => router.push(link.url!)}
          />
        ))}
      </AppShell.Navbar>
      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  )
}
