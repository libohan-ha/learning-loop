import {NavLink,Route,Routes,Navigate} from 'react-router-dom';
import {Layout,Menu,Typography} from 'antd';
import {HomeOutlined,PlayCircleOutlined,RedoOutlined,ExperimentOutlined} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';import Units from './pages/Units';import Reviews from './pages/Reviews';import Experiment from './pages/Experiment';import Unit from './pages/Unit';
const {Header,Content}=Layout;
const nav=[{key:'/today',icon:<HomeOutlined/>,text:'今日'},{key:'/units',icon:<PlayCircleOutlined/>,text:'单元'},{key:'/reviews',icon:<RedoOutlined/>,text:'复盘'},{key:'/experiment',icon:<ExperimentOutlined/>,text:'实验'}];
export default function App(){return <Layout className="shell"><Header className="header"><Typography.Title level={4} className="logo">学习闭环</Typography.Title><Menu theme="dark" mode="horizontal" items={nav.map(x=>({key:x.key,label:<NavLink to={x.key}>{x.icon} {x.text}</NavLink>}))}/></Header><Content className="content"><Routes><Route path="/" element={<Navigate to="/today"/>}/><Route path="/today" element={<Dashboard/>}/><Route path="/units" element={<Units/>}/><Route path="/units/:id" element={<Unit/>}/><Route path="/reviews" element={<Reviews/>}/><Route path="/experiment" element={<Experiment/>}/></Routes></Content></Layout>}
