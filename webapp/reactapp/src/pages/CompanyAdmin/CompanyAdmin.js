import { 
    Box,
    Button,
    Stack 
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate  } from 'react-router-dom';
import axios from 'axios';

function CompanyAdmin() {
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const cid = searchParams.get('cid');

    const [company, setCompany] = useState({
        name: '',
        branch: '',
        owner_name: '',
        owner_phone: '',
        owner_email: '',
        owner_position: '',
    });

    useEffect(() => {
        const initDataString = window.Telegram.WebApp.initData;
        let cid = searchParams.get('cid');

        axios.get(`/api/company/get/${cid}`, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            setCompany(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }, [cid]);

    const openEditor = () => {
        navigate({
            pathname: '/webapp/company/registration',
            search: `?cid=${cid}`,
        });
    }

    const openList = () => {
        navigate({
            pathname: '/webapp/company/ptlist',
            search: `?cid=${cid}`,
        });
    }

    const openHistory = () => {
        navigate({
            pathname: '/webapp/company/evlist',
            search: `?cid=${cid}`,
        });
    }
    
    return (
        <>
            <h1>Админка компании</h1> <br />
            <span>Управление компанией: {company.name}</span><br /><br /><br /><br />

            <Stack spacing={2}>
                <Box component={'span'} sx={{ display: 'block' }}>
                    Доступные оплаченные сборы: {company.payed_events}<br />
                    Участники компании: {company.employees_len}<br />
                    Создано сборов: {company.created_events_len}<br />
                    Успешные сборы: {company.succeded_events}<br />
                    Участники сборов: {company.participants_len}<br />
                    Количество переводов в сборах: {company.transfers}<br />
                    Сумма всех сборов: {company.events_sum}<br />
                    Средний чек: {company.avg_price}<br />
                    Открытые сборы: {company.open_events}
                </Box>

                <Stack spacing={2}>
                    <Button variant="contained" onClick={openEditor}>Изменить описание компании</Button>
                    <Button variant="contained" onClick={openList}>Редактировать список участников компании</Button>
                    <Button variant="contained" onClick={openHistory}>История сборов в компании</Button>
                </Stack>
            </Stack>

        </>
    )
}

export default CompanyAdmin;