interface IconProps {
  color?: string
}

const AnalyticsIcon = ({ color = '#818181' }: IconProps) => {
  return (
    <svg
      width="35"
      height="30"
      viewBox="0 0 35 30"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M13.611 0V24.2235H21.3887V0H13.611ZM19.2499 2.04968H15.7499V22.1739H19.2499V2.04968ZM1.94434 7.45341H9.7221V24.2235H1.94434V7.45341ZM4.08322 9.50311H7.58322V22.1739H4.08322V9.50311Z"
        fill={color}
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M35 27.9504H0V30.0001H35V27.9504Z"
        fill={color}
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M25.2773 11.1802H33.055V24.2236H25.2773V11.1802ZM27.4162 13.2299H30.9162V22.174H27.4162V13.2299Z"
        fill={color}
      />
    </svg>
  )
}

export default AnalyticsIcon
