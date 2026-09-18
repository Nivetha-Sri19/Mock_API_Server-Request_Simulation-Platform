import { Box, Typography } from "@mui/material";
function Inbox(){return <Box component="svg" viewBox="0 0 24 24" sx={{width:40,height:40,fill:"none",stroke:"currentColor",strokeWidth:1.6,strokeLinecap:"round",strokeLinejoin:"round"}}><path d="M4 4h16v16H4z"/><path d="M4 14h4l2 3h4l2-3h4"/></Box>}
export default function EmptyState({title,text}:{title:string;text:string}){return <Box sx={{py:7,textAlign:"center",color:"text.secondary"}}><Inbox/><Typography sx={{mt:1.5,fontWeight:800,color:"text.primary"}}>{title}</Typography><Typography sx={{mt:.5,fontSize:13}}>{text}</Typography></Box>}
