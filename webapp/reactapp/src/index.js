import React from 'react';
import ReactDOM from 'react-dom';
import {
  createBrowserRouter,
  RouterProvider
} from 'react-router-dom';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment'
import 'moment/locale/ru';
import './index.scss';
import UserRegistration from './pages/UserRegistration/UserRegistration';
import EventCreation from './pages/EventCreation/EventCreation';
import EventSharing from './pages/EventSharing/EventSharing';
import EventAdmin from './pages/EventAdmin/EventAdmin';
import EventParticipantsList from './pages/EventParticipantsList/EventParticipantsList';
import CompanyRegistration from './pages/CompanyRegistration/CompanyRegistration';
import CompanyAdmin from './pages/CompanyAdmin/CompanyAdmin';
import CompanyEventsList from './pages/CompanyEventsList/CompanyEventsList';
import CompanyParticipantsList from './pages/CompanyParticipantsList/CompanyParticipantsList';
import CompanySharing from './pages/CompanySharing/CompanySharing';

const root = ReactDOM.createRoot(document.getElementById('root'));

const router = createBrowserRouter([
  {
    path: '/webapp/userRegister',
    element: <UserRegistration />,
  },
  {
    path: '/webapp/eventCreateForm',
    element: <EventCreation />,
  },
  {
    path: '/webapp/shareEvent',
    element: <EventSharing />,
  },
  {
    path: '/webapp/eventAdmin',
    element: <EventAdmin />,
  },
  {
    path: '/webapp/eventParticipantsList',
    element: <EventParticipantsList />,
  },
  {
    path: '/webapp/company/registration',
    element: <CompanyRegistration />
  },
  {
    path: '/webapp/company/admin',
    element: <CompanyAdmin />
  },
  {
    path: '/webapp/company/evlist',
    element: <CompanyEventsList />
  },
  {
    path: '/webapp/company/ptlist',
    element: <CompanyParticipantsList />
  },
  {
    paht: '/webapp/company/share',
    element: <CompanySharing />
  }
]);

root.render(
  <LocalizationProvider dateAdapter={AdapterMoment} adapterLocale="ru">
    <RouterProvider router={router} />
  </LocalizationProvider>
);