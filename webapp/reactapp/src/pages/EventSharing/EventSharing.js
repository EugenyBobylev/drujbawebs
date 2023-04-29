import { useSearchParams } from "react-router-dom";
import styles from '../../fsuccess.module.scss';


function EventSharing() {
    // eslint-disable-next-line
    const [ searchParams, setSearchParams ] = useSearchParams();

    let link = `https://t.me/bot_druzhba_bot?start=e_${searchParams.get('eid')}`;

    return (
        <>
            <div className={ styles.sharewrap }>
                <div className={ styles.successInfo }>
                    <h1 className={ styles.h1 }>Поздравляем!</h1>
                    <p>Вы успешно создали сбор</p>
                    <p>Скопируйте эту ссылку и отправьте вашим друзьям для приглашения участников</p>
                    <p className={ styles.link }>{ link }</p>
                </div>
                <footer className={ styles.footer }>
                    <a href className="bottomBtn">Перейти к оплате</a>
                </footer>
            </div>
        </>
    )
}

export default EventSharing;