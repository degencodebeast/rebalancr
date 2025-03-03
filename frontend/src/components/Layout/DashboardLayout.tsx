'use client'

import { AppShell, Burger, Group, NavLink } from '@mantine/core'
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
  const { authenticated, ready } = usePrivy()

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
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header p="md">
        <Group justify="space-between">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <div className="logo">Rebalancr</div>
          <div></div> {/* Placeholder for right side header content */}
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md" className="sidenav_wrapper">
        {navLinks.map((link, index) => (
          <NavLink
            className="rounded-[10px] py-2 text-black"
            key={index}
            active={pathname.startsWith(link.url)}
            label={link.name}
            leftSection={link.icon}
            onClick={() => router.push(link.url)}
          />
        ))}
      </AppShell.Navbar>

      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  )
}
