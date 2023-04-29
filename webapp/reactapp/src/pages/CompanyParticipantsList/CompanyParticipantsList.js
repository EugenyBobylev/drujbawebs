import {
    Button,
    Grid,
    Stack,
    Box,
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

function CompanyParticipantsList() {
    const initDataString = window.Telegram.WebApp.initData;
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const [participants, setParticipants] = useState([]);

    let link = `https://t.me/bot_druzhba_bot?start=c_${searchParams.get('cid')}`;

    useEffect(() => {
        axios.get(`/api/company/getParticipants/${searchParams.get('cid')}`, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            setParticipants(response.data);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }, [initDataString]);

    const removeParticipant = (participant) => {
        console.log(participant);
        axios.post(`/api/company/removeParticipant/${searchParams.get('cid')}`, {
            uid: participant,
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


    return (
        <>
            <Box component={'span'} sx={{ display: 'block' }}>
                { link }
            </Box> <br /><br />

            <Stack spacing={2} direction={'column'}>
                {participants.map((participant) => (
                    <Grid container spacing={2}>
                        <Grid item xs={3}>
                            <span>{participant.name}</span>
                        </Grid>
                        <Grid item xs={3}>
                            <Button onClick={ () => removeParticipant(participant.tgid) } variant='contained'>Удалить</Button>
                        </Grid>
                    </Grid>
                ))}
            </Stack>

            <br /><br /><br /><br />

            <span>Вы можете передать права человеку, которого нет в списке.<br />Для этого отправьте ему ссылку на компанию и попросите зарегистрироваться.</span> <br />

            <Button onClick={ () => navigate(-1) } variant='contained'>Назад</Button>
        </>
    )
}

export default CompanyParticipantsList;