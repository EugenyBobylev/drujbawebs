import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate  } from 'react-router-dom';
import axios from 'axios';
import styles from './companyEventsList.module.scss';

function CompanyEventsList() {
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const cid = searchParams.get('cid');

    const [showOpened, setShowOpened] = useState(true);
    const [showClosed, setShowClosed] = useState(false);
    const [showSucceded, setShowSucceded] = useState(true);
    const [showUnsucceded, setShowUnsucceded] = useState(true);

    const [events, setEvents] = useState([]);

    useEffect(() => {
        const initDataString = window.Telegram.WebApp.initData;

        axios.get(`/api/company/getEvents/${cid}`, {
            headers: {
                'Authorization': btoa(initDataString),
            }, params: {
                showOpened: showOpened,
                showClosed: showClosed,
                showSucceded: showSucceded,
                showUnsucceded: showUnsucceded
            }
        }).then(function (response) {
            setEvents(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }, [cid, showOpened, showClosed, showSucceded, showUnsucceded]);

    const openEvent = (eid) => {
        navigate({
            pathname: '/webapp/eventAdmin',
            search: `?eid=${eid}`
        });
    }

    const handleShowOpened = () => {
        setShowOpened(!showOpened);
    };
    const handleShowClosed = () => {
        setShowClosed(!showClosed);
    };
    const handleShowSucceded = () => {
        setShowSucceded(!showSucceded);
    };
    const handleShowUnsucceded = () => {
        setShowUnsucceded(!showUnsucceded);
    };

    return (
        <>
            
            <div className={styles.eventlist}>
                <h1>Список сборов</h1>
                <div className={styles.companyInfo}>
                    <a onClick={handleShowOpened} className={ showOpened ? styles.active : '' }>
                        <div className={styles.buttonInfo}>
                            { showOpened ? (<img src="./mark.svg" alt="" />) : ''}
                            <p>Открытые</p>
                        </div>
                        {/* <p>5</p> */}
                    </a>
                    <a onClick={handleShowClosed} className={ showClosed ? styles.active : '' }>
                        <div className={styles.buttonInfo}>
                            { showClosed ? (<img src="./mark.svg" alt="" />) : ''}
                            <p>Закрытые</p>
                        </div>
                        {/* <p>7</p> */}
                    </a>
                    <a onClick={handleShowSucceded} className={ showSucceded ? styles.active : '' }>
                        <div className={styles.buttonInfo}>
                            { showSucceded ? (<img src="./mark.svg" alt="" />) : ''}
                            <p>Успешные</p>
                        </div>
                        {/* <p>4</p> */}
                    </a>
                    <a onClick={handleShowUnsucceded} className={ showUnsucceded ? styles.active : '' }>
                        <div className={styles.buttonInfo}>
                            { showUnsucceded ? (<img src="./mark.svg" alt="" />) : ''}
                            <p>Неуспешные</p>
                        </div>
                        {/* <p>83</p> */}
                    </a>
                </div>
                <ul>
                    {events.map((event) => (
                        <li>
                            <div className={styles.info}>
                                <p>{ event.target }</p>
                                <p>{ event.campaign_start }</p>
                            </div>
                            <a onClick={() => openEvent(event.id)} />
                        </li>
                    ))}
                </ul>
                <footer>
                    <a onClick={ () => navigate(-1) } className={styles.bottomBtn}>Назад</a>
                </footer>
            </div>


        </>
    )
}

export default CompanyEventsList;