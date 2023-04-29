import {
    Box,
    Button,
    Grid
} from '@mui/material'
import { useSearchParams } from "react-router-dom";

function CompanyInvite() {
    // eslint-disable-next-line
    const [ searchParams, setSearchParams ] = useSearchParams();
    
    let link = `https://t.me/bot_druzhba_bot?start=c_${searchParams.get('cid')}`;

    return (
        <>
            <span>Поздравляю, вы успешно подключили компанию к сервису. Теперь мы дружим :)</span><br /><br />
            <span>Скопируйте эту ссылку и отправьте друзьям или коллегам, которые будут участвовать в сборах вашей компании. Они внесут свои данные, и я смогу автоматически напоминать им о событиях, получать информацию о переводах и передавать её вам.</span><br /><br /><br /><br />

            <Grid container spacing={2}>
                <Grid item xs={3}>
                    <span>Ссылка на сбор: </span>
                </Grid>
                <Grid item xs={9}>
                    <Box component='span' sx={{ display: 'block' }}>{link}</Box>
                </Grid>
            </Grid>
            <br /><br />
            <Button onClick={ () => window.Telegram.WebApp.close() } variant='contained'>Проверить ваш тариф или перейти к оплате</Button>
        </>
    )
}

export default CompanyInvite;