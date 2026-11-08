import * as _ from 'lodash';
import moment from 'moment';
import { FaHome, FaUser, FaCog, FaBell, FaSearch, FaStar } from 'react-icons/fa';

export function App() {
  const when = moment().format('LL');
  return <div>{_.capitalize('today')} {when} <FaHome /></div>;
}
