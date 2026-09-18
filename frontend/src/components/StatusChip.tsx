import { Chip } from "@mui/material";
export default function StatusChip({active,label}:{active:boolean;label?:string}){return <Chip size="small" label={label || (active?"ACTIVE":"INACTIVE")} color={active?"success":"default"} variant="outlined"/>}
