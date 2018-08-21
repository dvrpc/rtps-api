import {headerRender} from './modules/header/header';
import {HeaderElements} from "./modules/header/HeaderElements";
import {Map} from './modules/map/map'
import {Footer} from './modules/footer/footer';
import './css/app.css'


headerRender(HeaderElements);
let map = new Map();
let footer = new Footer();

export {map};