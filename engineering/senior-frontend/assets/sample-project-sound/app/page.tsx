import { format } from 'date-fns';

export default function Home() {
  return <main>Today is {format(new Date(), 'PPP')}</main>;
}
