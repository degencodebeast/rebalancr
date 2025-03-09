'use client'

export default function FlowDiagram() {
  const steps = [
    { id: 1, label: 'Connect Wallet', color: '#8C52FF' },
    { id: 2, label: 'Deposit Assets', color: '#121212' },
    {
      id: 3,
      label: 'Customize AI',
      color: '#8C52FF',
    },
    { id: 4, label: 'Automation', color: '#121212' },
    { id: 5, label: 'Generate Yield', color: '#8C52FF' },
  ]

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4">
      <div className="flex flex-col items-center max-w-md w-full py-8">
        {steps.map((step, index) => (
          <div key={step.id} className="w-full flex flex-col items-center">
            <button
              className={`bg-[${step.color}] text-white font-normal md:py-10 py-6 rounded-[50px] w-full md:text-[24px] text-[19px]`}
            >
              {step.label}
            </button>

            {/* Arrow connecting to next step (except for the last one) */}
            {index < steps.length - 1 && (
              <div className="flex flex-col items-center my-2">
                <div className="h-10 w-0.5 bg-black"></div>
                <svg
                  width="10"
                  height="6"
                  viewBox="0 0 10 6"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path d="M5 6L0 0H10L5 6Z" fill="black" />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
