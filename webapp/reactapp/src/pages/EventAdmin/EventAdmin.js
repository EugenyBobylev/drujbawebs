import { 
    Box,
    Button,
    Stack 
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate  } from 'react-router-dom';
import axios from 'axios';
import styles from './eventAdmin.module.scss';

function EventAdmin() {
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    
    const eid = searchParams.get('eid');

    const [event, setEvent] = useState({
        target: '',
        campaign_start: '',
        closed: false,
        type: '',
        participants: [],
        participants_info: [],
        payed_summ: 0,
        avg_price: 0
    });

    
    useEffect(() => {
        const initDataString = window.Telegram.WebApp.initData;
        let eid = searchParams.get('eid');

        axios.get(`/api/getEvent/${eid}`, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            setEvent(response.data);
            console.log(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }, [eid]);

    const openShare = () => {
        navigate({
            pathname: '/webapp/shareEvent',
            search: `?eid=${eid}&target=${event.target}`,
        });
    }

    const openEditor = () => {
        navigate({
            pathname: '/webapp/eventCreateForm',
            search: `?eid=${eid}`
        }); 
    }

    const openList = () => {
        navigate({
            pathname: '/webapp/eventParticipantsList',
            search: `?eid=${eid}`
        });
    }


    return (
        <>
            <div className={ styles.eventadmin }>
                <header>
                    <div className={ styles.headerContainer }>
                        <p>Управление сбором</p>
                        <h1>{ event.target }</h1>
                    </div>
                    <a href className={ styles.notificationIcon } />
                </header>
                <p className={ styles.smallParagraph }>{ event.campaign_start }</p>
                <div className={ styles.companyButtons }>
                    <a onClick={openShare}>
                        <img src="./linkIcon.svg" alt="" />
                        <p>Ссылка на сбор</p>
                    </a>
                    <a onClick={openEditor}>
                        <img src="./mini-icons (2).svg" alt="" />
                        <p>Изменить детали сбора</p>
                    </a>
                    <a onClick={openList}>
                        <img src="./mini-icons.svg" alt="" />
                        <p>Редактировать список участников</p>
                    </a>
                </div>
                <div className={ styles.companyInfo }>
                    <ul>
                        <li>
                            <p>Сбор открыт</p>
                            <p>{event.closed ? 'Нет' : 'Да'}</p>
                        </li>
                    </ul>
                    <ul>
                        <li>
                            <p>Тип события</p>
                            <p>{ event.type }</p>
                        </li>
                        <li>
                            <p>На кого</p>
                            <p>{ event.target }</p>
                        </li>
                        <li>
                            <p>Дата</p>
                            <p>{ event.campaign_start }</p>
                        </li>
                        {/* <li>
                            <p>Осталось дней</p>
                            <p>5</p>
                        </li> */}
                    </ul>
                    <ul>
                        <li>
                            <p>Сдали деньги</p>
                            <p>{ event.participants_info.len } человек</p>
                        </li>
                        <li>
                            <p>Сумма сбора</p>
                            <p>{ event.payed_summ } р.</p>
                        </li>
                        <li>
                            <p>Средний чек</p>
                            <p>{ event.avg_price } р.</p>
                        </li>
                    </ul>
                </div>
                <footer>
                    <a onClick={ window.Telegram.WebApp.close } className={ styles.bottomBtn }>Закрыть</a>
                </footer>
            </div>
        </>
    )
}

export default EventAdmin;