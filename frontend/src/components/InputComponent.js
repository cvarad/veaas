import React, { useState } from 'react';

const InputComponent = (props) => {
    const [selectedOperations, setSelectedOperations] = useState({
        "trim": {
            "isChecked": false,
            "title": "Trim",
            "operation": "trim",
            "operation_args": {
                "start_time": 0,
                "end_time": 100,
            },
        },
        "hflip": {
            "isChecked": false,
            "title": "Horizontal Flip",
            "operation": "hflip",
            "operation_args": {},
        },
        "vflip": {
            "isChecked": false,
            "title": "Vertical Flip",
            "operation": "vflip",
            "operation_args": {},
        },
        "drawbox": {
            "isChecked": false,
            "title": "Drawbox",
            "operation": "drawbox",
            "operation_args": {
                "x": 0,
                "y": 0,
                "width": 0,
                "height": 0,
                "color": 0,
                "thickness": 0,
            },
        },
    })

    const onChange = (operation_name, key, event) => {
        const selectedOperationsCopy = Object.assign({}, selectedOperations);
        selectedOperationsCopy[operation_name]['operation_args'][key] = event.target.value;
        console.log(selectedOperations);
        setSelectedOperations(selectedOperationsCopy);
        console.log(selectedOperations);
        updateParentState();
    }

    const onCheckToggle = (operation_name) => {
        const selectedOperationsCopy = Object.assign({}, selectedOperations);
        selectedOperationsCopy[operation_name]['isChecked'] = !selectedOperationsCopy[operation_name]['isChecked'];
        console.log(selectedOperations);
        
        setSelectedOperations(selectedOperationsCopy);
        console.log(selectedOperations)
        updateParentState();
    }

    const updateParentState = () => {
        let parentState = []
        Object.entries(selectedOperations).map(([operation_name, operation]) => {
            if (operation.isChecked) {
                parentState.push({
                    'operation': operation.operation,
                    'operation_args': operation.operation_args,
                })
            }
        })
        props.onInputChange(parentState)
        console.log(parentState)
    }

    const renderOperationInput = (operation_name, operation) => (
        <div key={operation.title}>
            <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                <input type='checkbox' onChange={() => onCheckToggle(operation_name)}></input>
                <p>{operation.title}</p>
            </div>
            {operation.isChecked ? <div style={{ display: 'flex', flexDirection: 'row', }}>
                {Object.entries(operation.operation_args).map(([key, value]) => (
                    <div key={operation_name + key}>
                        <p>{key}</p>
                        <input value={value} type='text' onChange={(event) => onChange(operation_name, key, event)}></input>
                    </div>
                ))}
            </div> : null}
        </div>
    )

    return (
        <>
            <form>
                {
                    Object.entries(selectedOperations).map(([operation_name, operation]) => {
                        return renderOperationInput(operation_name, operation);
                    })
                }
            </form>
        </>
    );
}

export default InputComponent;