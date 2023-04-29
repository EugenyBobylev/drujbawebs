import { useForm, Controller } from 'react-hook-form';
import axios from 'axios';
import { useSearchParams, useNavigate } from "react-router-dom";
import { useEffect, useState, useRef } from 'react';
import styles from './userRegistration.module.css';
import woman from './woman.svg';

function UserRegistration() {
    // eslint-disable-next-line
    const [ searchParams, setSearchParams ] = useSearchParams();
    const navigate = useNavigate();

    const { handleSubmit, register, control } = useForm({
        defaultValues: {
            name: '',
            dob: null,
            timezone: 0,
            pdata: false
        }
    });

    const onSubmit = (data) => { 
        const initDataString = window.Telegram.WebApp.initData;

        if (searchParams.get('cid')) data.cid = searchParams.get('cid');
        if (searchParams.get('eid')) data.eid = searchParams.get('eid');

        axios.post('/api/userRegister', data, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            if (searchParams.get('deeplink')) {
                navigate(searchParams.get('deeplink'));
                return;
            }

            window.Telegram.WebApp.close();
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }

    useEffect(() => {
        const initDataString = window.Telegram.WebApp.initData;
        axios.get('/api/userData', {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            if (searchParams.get('deeplink')) {
                navigate(searchParams.get('deeplink'));
                return;
            } else {
                window.Telegram.WebApp.close();
            }
        }).catch(function (error) {
            return;
        });

        dateInput.current.style.transform = `scaleX(${dateInput.current.nextElementSibling.offsetWidth})`;
    }, [searchParams]);

    const [sdate, setSdate] = useState('Дата рождения');

    const dateInput = useRef(null);

    return (
        <>
            <img className={ styles.img } src={woman} />
            <h1 className={ styles.h1 }>Регистрация</h1>
            <p className={ styles.p }>
                Пожалуйста, введите данные для регистрации. После этого вы сможете начать сбор
            </p>

            <form onSubmit={handleSubmit(onSubmit)}>
                <div className={ styles.qweqwe }>
                    <input type='text' placeholder='Имя и фамилия' className='required' required {...register('name')} />

                    <div className={ styles.dateinput }>
                        
                        <Controller
                            name='dob'
                            control={control}
                            rules={{ required: true }}
                            render={({  field: { onChange, value } }) => (
                                <input ref={ dateInput } id='birthday' type='date' name='birthday' required onChange={ (event) => { setSdate(!event.target.value ? 'Дата рождения' : event.target.value.split('-')[2] + '.' + event.target.value.split('-')[1] + '.' + event.target.value.split('-')[0]); onChange(event); }} value={ value }/>
                            )}
                        />

                        <label for='birthday'>{ sdate }</label>
                    </div>
                    <select name="timezone" {...register('timezone')}>
                        <option value={-1.0} selected>Калининградское время (МСК -1)</option>
                        <option value={0.0}>Московское время (МСК)</option>
                        <option value={1.0}>Самарское время (МСК +1)</option>
                        <option value={2.0}>Екатеринбургское время (МСК +2)</option>
                        <option value={3.0}>Омское время (МСК +3)</option>
                        <option value={4.0}>Красноярское время (МСК +4)</option>
                        <option value={5.0}>Иркутское время (МСК +5)</option>
                        <option value={6.0}>Якутское время (МСК +6)</option>
                        <option value={7.0}>Владивостокское время (МСК +7)</option>
                        <option value={8.0}>Магаданское время (МСК +8)</option>
                        <option value={9.0}>Самарское время (МСК +9)</option>
                    </select>

                    <div className={ styles.formfooter }>
                        <input type='checkbox' id='check' required {...register('pdata')} />
                        <label for='check'>Я согласен на обработку моих персональных данных в соответствии с <a href=''>Политикой и Пользовательским соглашением</a></label>
                        <button type='submit'>Сохранить</button>
                    </div>
                </div>
            </form>
        </>
    )
}

export default UserRegistration;