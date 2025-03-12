import DashboardLayout from '@/components/Layout/DashboardLayout'
import { Button } from '@/components/ui/button'

const Support = () => {
  return (
    <DashboardLayout>
      <div className="flex flex-col gap-4 px-10 py-10">
        <h1 className="text-[32px] font-medium">
          Chat with our Telegram Support Bot
        </h1>

        <ul className="list-disc marker:text-[#8C52FF] pl-6 space-y-4 max-w-[680px] text-[20px]">
          <li>
            24/7 AI Powered Telegram Chatbot. Human response available 9am UTC -
            10AM UTC
          </li>
          <li>
            Tailored to answer all questions about Rebalancr and provide
            solutions to all issues you might be facing with the dashboard.
          </li>
          <li>
            Do not share your seedphrase or private key while chatting with the
            telegram bot. For Any serious challenges you might be facing,
            contact us - rebalancr.org@gmail.com
          </li>
        </ul>

        <Button className="w-fit bg-[#8C52FF] text-white py-4 px-10 rounded-full text-[20px] mt-6">
          Continue
        </Button>
      </div>
    </DashboardLayout>
  )
}

export default Support
