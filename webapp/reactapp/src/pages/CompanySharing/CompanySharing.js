import { useSearchParams } from "react-router-dom";
import styles from '../../fsuccess.module.scss';


function CompanySharing() {
    // eslint-disable-next-line
    const [ searchParams, setSearchParams ] = useSearchParams();

    let link = `https://t.me/bot_druzhba_bot?start=c_${searchParams.get('cid')}`;

    return (
        <>
            <div className={ styles.sharewrap }>
                <div className={ styles.successInfo }>
                    <h1 className={ styles.h1 }>Поздравляем!</h1>
                    <p>Вы успешно подключили компанию к сервису. Теперь мы дружим :)</p>
                    <p>Скопируйте эту ссылку и отправьте друзьям или коллегам, которые будут участвовать в сборах вашей компании.
            Они внесут свои данные, и я смогу автоматически напоминать им о событиях, получать информацию о переводах и
            передавать её вам.</p>
                    <p className={ styles.link }>{ link }</p>
                </div>
                <footer className={ styles.footer }>
                    <a href className="bottomBtn">Перейти к оплате</a>
                </footer>
            </div>
        </>
    )
}

export default CompanySharing;