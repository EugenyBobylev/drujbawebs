import {
    Button,
    Grid,
    Stack,
    Box,
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './participantList.module.css';
// import './participantList.css'

function EventParticipantsList() {
    const initDataString = window.Telegram.WebApp.initData;
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const [participants, setParticipants] = useState([]);

    let link = `https://t.me/bot_druzhba_bot?start=e_${searchParams.get('eid')}`;

    useEffect(() => {
        axios.get(`/api/getEventParticipants/${searchParams.get('eid')}`, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            setParticipants(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });

        // let startX, movingX, deltaX;
        // let infos = document.getElementsByClassName("participantInfo")
        // let mouseDown = false;
        // for (let participantInfo of infos) {
        //     participantInfo.ontouchstart = (event) => {
        //         touchStart(event, participantInfo)
        //     }
        //     participantInfo.ontouchmove = (event) => {
        //         touchMove(event, participantInfo)
        //     }
        //     participantInfo.ontouchend = () => {
        //         touchEnd(participantInfo)
        //     }
        //     participantInfo.onmousedown = (event) => {
        //         mouseDown = true
        //         mouseStart(event, participantInfo)
        //     }
        //     participantInfo.onmousemove = (event) => {
        //         if (mouseDown) {
        //             mouseMove(event, participantInfo)
        //         }
        //     }
        //     participantInfo.onmouseup = () => {
        //         mouseDown = false
        //         touchEnd(participantInfo)
        //     }
        // }

        // function touchStart(e, participantInfo) {
        //     participantInfo.style.transition = "0s"
        //     startX = e.touches[0].clientX
        // }

        // function touchMove(e, participantInfo) {
        //     e.stopPropagation();
        //     movingX = e.touches[0].clientX
        //     deltaX = movingX - startX
        //     if (deltaX <= -48) {
        //         deltaX = -48
        //     }
        //     if (deltaX < 0) {
        //         participantInfo.style.transform = "translateX(" + deltaX + "px)"
        //     }
        // }

        // function touchEnd(participantInfo) {
        //     if (deltaX <= -48) {
        //         setTimeout(() => {
        //             participantInfo.style.transition = "0.3s"
        //             participantInfo.style.transform = "translateX(-" + 0 + "px)"
        //         }, 1000)
        //     } else {
        //         participantInfo.style.transition = "0.3s"
        //         participantInfo.style.transform = "translateX(-" + 0 + "px)"
        //     }

        // }

        // function mouseStart(e, participantInfo) {
        //     participantInfo.style.transition = "0s"
        //     startX = e.clientX
        // }

        // function mouseMove(e, participantInfo) {
        //     e.stopPropagation();
        //     movingX = e.clientX
        //     deltaX = movingX - startX
        //     if (deltaX <= -48) {
        //         deltaX = -48
        //     }
        //     if (deltaX < 0) {
        //         participantInfo.style.transform = "translateX(" + deltaX + "px)"
        //     }
        // }
    }, [searchParams]);

    const removeParticipant = (participant) => {
        axios.post(`/api/removeParticipant/${searchParams.get('eid')}`, {
            participant: participant,
        }, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            setParticipants(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }

    const transferOwnership = (participant) => {
        axios.post(`/api/transferOwnership/${searchParams.get('eid')}`, {
            participant: participant,
        }, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            window.Telegram.WebApp.close();
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }

    return (
        <>
            <span>Здесь вы можете передать свои права или удалить участника из сбора. Например, если он не хочет участвовать.</span><br /><br />

            <Stack spacing={2}>
                {participants.map((participant) => (
                    <Grid container spacing={2}>
                        <Grid item xs={3}>
                            <span>{participant.name}: {participant.payed} руб.</span>
                        </Grid>
                        <Grid item xs={3}>
                            <Button onClick={ () => removeParticipant(participant.id) } variant='contained'>Удалить</Button>
                        </Grid>
                        <Grid item xs={3}>
                            <Button onClick={ () => transferOwnership(participant
                                .id) } sx={{ display: participant.id === window.Telegram.WebApp.initDataUnsafe.user.id ? 'block' : 'none' }} variant='contained'>Передать права</Button>
                        </Grid>
                    </Grid>
                ))}
            </Stack>

            <br /><br /><br /><br />
            <span>Вы можете передать права человеку, которого нет в списке. Для этого отправьте ему ссылку на сбор и попросите подключиться.<br />Ссылка на сбор:</span>

            <Box component={'span'} sx={{ display: 'block' }}>
                { link }
            </Box>

            <Button onClick={ () => navigate(-1) } variant='contained'>Назад</Button>

            {/* <h1 className={styles.title}>Список <br /> участников</h1>
            <ul>
                {participants.map((participant) => (
                    <li className={styles.ulli}>
                        <div className={styles.participantInfo} >
                            <section>
                                <p>{ participant.name }</p>
                            </section>
                            <section>
                                <a onClick={ () => transferOwnership(participant
                                .id) } style={{ display: participant.id === window.Telegram.WebApp.initDataUnsafe.user.id ? 'block' : 'none' }}>Назначить админом</a>
                            </section>
                        </div>
                        <a className={styles.ullia} onClick={ () => removeParticipant(participant.id) }></a>
                    </li>
                ))}
            </ul>
            <div className={styles.participantSection}>
                <p className={styles.topParagraph}>Вы можете также передать права администратора сбора человеку, которого нет в списке.
                    Для
                    этого отправьте ему ссылку на компанию и попросите зарегистрироваться.</p>
                <p className={styles.smallParagraph}>Ссылка на подключение к сбору</p>
                <p className={styles.linkParagraph}>{ link }</p>
            </div>
            <footer className={styles.footer}>
                <a onClick={ () => navigate(-1) } className={styles.bottomBtn}>Назад</a>
            </footer> */}

        </>
    )
}

export default EventParticipantsList;