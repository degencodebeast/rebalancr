interface IconProps {
  color?: string
}

const HistoryIcon = ({ color = '#818181' }: IconProps) => {
  return (
    <svg
      width="26"
      height="30"
      viewBox="0 0 26 30"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7.25054 7.66411C4.8378 9.10789 0.512602 13.7502 2.51377 20.7693C4.64765 28.2538 13.1105 28.949 16.3518 27.8217C19.7048 26.6555 24.2033 24.1066 23.856 15.0496C23.558 7.27539 17.0968 3.11061 13.9035 2C14.1874 4.75801 13.531 10.8515 8.63448 13.1616C8.29742 12.8469 7.63391 11.9955 7.67649 11.107"
        stroke={color}
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default HistoryIcon
