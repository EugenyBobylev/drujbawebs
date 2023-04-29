import { useNavigate, useSearchParams } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { 
    Button,
    FormControl,
    FormGroup,
    TextField 
} from "@mui/material";
import axios from 'axios';
import { useEffect, useState, useRef } from 'react';
import styles from './companyRegistration.module.scss';


function CompanyRegistration() {
    // eslint-disable-next-line
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const isEditing = searchParams.get('cid') === null ? false : true;

    const { handleSubmit, control, setValue, register } = useForm({
        defaultValues: {
            name: '',
            branch: '',
            peoplenum: 0,
            personName: '',
            position: '',
            phone: '',
            email: '',
        }
    });

    const onSubmit = (data) => {
        const initDataString = window.Telegram.WebApp.initData;

        if (isEditing) data.cid = searchParams.get('cid');

        axios.post('/api/company/register', data, {
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
        if (isEditing) {
            const initDataString = window.Telegram.WebApp.initData;

            axios.get(`/api/company/get/${searchParams.get('cid')}`, {
                headers: {
                    'Authorization': btoa(initDataString),
                }
            }).then(function (response) {
                setValue('name', response.data.name);
                setValue('branch', response.data.branch);
                setValue('personName', response.data.owner_name);
                setValue('position', response.data.owner_position);
                setValue('phone', response.data.owner_phone);
                setValue('email', response.data.owner_email);
            }).catch(function (error) {
                console.log(error);
                window.Telegram.WebApp.showPopup({ message: 'Что-то пошло не так. Попробуйте позже.' });
            });
        }
        
        let inputs = formRef.current.querySelectorAll('input');

        for (let i of inputs) { 
            i.onclick = function() {
                this.previousElementSibling.style.transform = 'none'
                this.previousElementSibling.style.fontSize = "10px"
            }
            i.onblur = function() {
                if (this.value == "") {   
                    this.previousElementSibling.style.transform = 'translate(13px, 31px)'
                    this.previousElementSibling.style.fontSize = "14px"
                }
            }
        }


    }, []);        
    
    const formRef = useRef(null);

    return (
        <>
            
            <h1 className={ styles.h1 }>Регистрация <br /> компании</h1>
            <form ref={ formRef } name="companyRegistrationForm" className={ styles.form }>
                <p className={ styles.smallparagraph }>Название компании *</p>
                <input type="text" placeholder className="required" required {...register('name')} />
                <p className={ styles.smallparagraph }>Сфера деятельности *</p>
                <input type="text" placeholder className="required" required {...register('branch')} />
                <p className={ styles.smallparagraph }>Количество человек в компании *</p>
                <input type="number" placeholder className="required" required {...register('peoplenum')} />
                <p className={ styles.smallparagraph }>Ваши имя и фамилия *</p>
                <input type="text" placeholder className="required" required {...register('personName')} />
                <p className={ styles.smallparagraph }>Должность</p>
                <input type="text" placeholder className="required" {...register('position')} />
                <p className={ styles.smallparagraph }>Контактный телефон *</p>
                <input type="tel" placeholder className="required" required {...register('phone')} />
                <p className={ styles.smallparagraph }>E-mail *</p>
                <input type="email" placeholder className="required" required {...register('name')} />
            </form>
            <footer className={ styles.formfooter }>
                <a href onClick={ handleSubmit(onSubmit) } className={ styles.bottombtn }>Сохранить</a>
            </footer>

        </>
    )
}

export default CompanyRegistration;
