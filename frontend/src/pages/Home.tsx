import { Link } from '@tanstack/react-router'
// import { useAuth } from '../contexts/auth.context'
import demoGif from '../assets/demo_gif.gif'
import AlertModal from '../components/AlertModal'
import { useState } from 'react'

const Home = (): JSX.Element => {
  // const authState = useAuth()
  const [disclaimerIsOpen, setDisclaimerIsOpen] = useState(true)

  return (
    <div className='bg-gradient-to-b from-blue-500 h-full'>
      <AlertModal title={'Importante'} isOpen={disclaimerIsOpen} close={() => { setDisclaimerIsOpen(false) }} disclaimer={true}>
        <div className="prose text-md">
        <p className="mb-0">Planner es todavía una <span className="font-semibold">plataforma experimental</span>.</p>
        <ul className='list-disc pl-5 mt-0'>
          <li>Las mallas validadas pueden tener errores.
            <ul>
              <li>Revisa manualmente que la malla haga sentido.</li>
              <li>Recuerda que SIDING es la referencia oficial.</li>
            </ul>
          </li>
          <li>Algunas mallas curriculares todavía no han sido cargadas. Esto está en curso.</li>
          <li>Por ahora, el login UC está deshabilitado, así que debes ingresar tus cursos manualmente.</li>
        </ul>
        </div>
      </AlertModal>
      <div className="max-w-3xl mx-auto mt-8 prose center">
          <h1 className='text-white text-center font-medium'>Bienvenido al Nuevo Planner, el lugar donde puedes planificar tu carrera universitaria</h1>
          <div className='flex justify-evenly'><Link to="/planner/new"><button className='rounded-lg py-2 px-4 bg-blue-800 text-white'>Planificar Malla</button></Link></div>
                {
                /* authState?.user != null
                  ? (<div className='flex justify-evenly'><Link to="/user"><button className='rounded-lg py-2 px-4 bg-blue-800 text-white'>Mis mallas</button></Link></div>)
                  : (<div className='flex justify-evenly'><a href="/api/user/login"><button className='rounded-lg py-2 px-4 bg-blue-800 text-white'>Iniciar sesión</button></a><Link to="/planner/new"><button className='rounded-lg py-2 px-4 bg-blue-800 text-white'>Continuar como invitado</button></Link></div>)}
                */}
            </div>
      <img className="w-auto m-5 mx-auto h-3/5" alt="demo" src={demoGif}></img>
    </div>
  )
}

export default Home
