import {
    FormControl, 
    FormGroup,
    TextField,
    Button,
    Stack
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { useForm, Controller } from 'react-hook-form';
import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import styles from './eventCreation.module.scss';

function EventCreation() {
    const initDataString = window.Telegram.WebApp.initData;
    const navigate = useNavigate();
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();

    const isEditing = searchParams.get('eid') === null ? false : true;

    const { handleSubmit, control, setValue, register } = useForm({
        defaultValues: {
            type: '',
            target: '',
            date: null,
            reciever: '',
            gifts: ''
        }
    });

    const dateInput = useRef(null);
    const presents = useRef(null);
    const [sdate, setSdate] = useState('Дата рождения');

    const onSubmit = (data) => {
        if (isEditing) data.eid = searchParams.get('eid');
        axios.post('/api/eventCreation', data, {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            if (isEditing) {
                navigate(-1);
            } else {
                navigate({
                    pathname: '/webapp/shareEvent',
                    search: `?eid=${response.data.event_id}&target=${data.target}`,
                });
            }
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
        });
    }

    const cancel = () => {
        if (isEditing) {
            navigate(-1);
        } else {
            window.Telegram.WebApp.close();
        }
    }

    const [tariff, setTariff] = useState(0); // 0 - free and has, 1 - free and not, 2 - premium

    useEffect(() => {
        axios.get('/api/userData', {
            headers: {
                'Authorization': btoa(initDataString),
            }
        }).then(function (response) {
            if (response.data.payed_events === 0) { setTariff(1); return; }
            if (response.data.premium === false) { setTariff(0); return; }
            setTariff(2);
        }).catch(function (error) {
            console.log(error);
            window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
            window.Telegram.WebApp.close();
        });

        if (isEditing) {
            axios.get(`/api/getEvent/${searchParams.get('eid')}`, {
                headers: {
                    'Authorization': btoa(initDataString),
                }
            }).then(function (response) {
                console.log(response.data);
                setValue('type', response.data.type);
                setValue('target', response.data.target);
                setValue('date', response.data.date);
                setValue('reciever', response.data.recieve_link);
                setValue('gifts', response.data.gifts_example);
            }).catch(function (error) {
                console.log(error);
                window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
            });
        }

        dateInput.current.style.transform = "scaleX(" + (dateInput.current.nextElementSibling.offsetWidth) + ")";
    });

    let startButton;

    if (isEditing) {
        startButton = <Button onClick={handleSubmit(onSubmit)} variant='contained'>Сохранить изменения</Button>;
    } else if (tariff === 0) {
        startButton = <Button onClick={handleSubmit(onSubmit)} variant='contained'>Запустить бесплатно</Button>;
    } else if (tariff === 1) {
        startButton = <Button onClick={handleSubmit(onSubmit)} variant='contained'>Оплатить и запустить сбор</Button>;
    } else if (tariff === 2) {
        startButton = <Button onClick={handleSubmit(onSubmit)} variant='contained'>Запустить</Button>;
    }

    const addingOptions = useRef(null);
    const addingCheckbox = useRef(null);

    const toggleCelebration = () => {
        console.log(addingCheckbox.current.checked);
        if (addingCheckbox.current.checked) {
            addingOptions.current.style.display = 'block';
            presents.current.style.marginBottom = '400px';
        } else {
            addingOptions.current.style.display = 'none';
            presents.current.style.marginBottom = '200px';
        }
    }

    return (
        <>
            <h1 className={ styles.h1 }>Создание сбора</h1>
            <p className={ styles.p }>Пожалуйста, заполните данные о сборе</p>
            <form onSubmit={ handleSubmit(onSubmit) } name="feeCreationForm" className={ styles.form }>
                <input type="text" placeholder="Тип события" required {...register('type')}/>
                <input type="text" placeholder="Кому собираем" required {...register('target')}/>

                <div className={ styles.dateInput }>

                    <Controller
                        name='date'
                        control={control}
                        rules={{ required: true }}
                        render={({ field: { onChange, value } }) => (
                            <input ref={ dateInput } type="date" onChange={ (event) => { setSdate(!event.target.value ? 'Дата рождения' : event.target.value.split('-')[2] + '.' + event.target.value.split('-')[1] + '.' + event.target.value.split('-')[0]); onChange(event); }} value={ value } name="birthday" required />
                        )}
                    />

                    <label htmlFor="birthday">{ sdate }</label>
                </div>

                <input type="text" placeholder="Ссылка на внешнюю копилку/карту" required {...register('reciever')}/>
                <p className={ styles.smallParagraph }>Ссылки на желаемый подарок
                *</p>
                <div ref={ presents } className={ styles.presents }>
                    <div className={ styles.present } id="present0">
                        <input type="text" placeholder="Ссылка" defaultValue required />
                        <button onclick="addPresent(event)" type="button" />
                    </div>
                </div>
                <div className={ styles.formfooter }>
                    <div className={ styles.formAdding }>
                        <input ref={ addingCheckbox } className="addingCheckbox" type="checkbox" name="check" id="addingCheckbox" onChange={ toggleCelebration } />
                        <label htmlFor="addingCheckbox">Добавить данные о праздновании</label>
                        <div ref={ addingOptions } className={ styles.addingOptions }>
                            <input type="text" placeholder="Дата события" />
                            <input type="text" placeholder="Время" />
                            <input type="text" placeholder="Ссылка на место празднования" />
                            <input type="text" placeholder="Дресс-код" />
                        </div>
                    </div>
                    <div className={ styles.formButtons }>
                        <button onClick={ () => cancel() } type="button">Отмена</button>
                        <button type='submit' className={ styles.middleBtn }>Запустить</button>
                        <button>Оплатить</button>
                    </div>
                </div>
            </form>
        </>
    )
}

export default EventCreation;