import numpy as np


__all__ = ["quality_cut"]


def _delete_particles(event_obj, idx_arr) -> None:
    #list of attributes
    attr_list = [a for a in dir(event_obj) if not a.startswith("__") and not callable(getattr(event_obj, a))]
    for attr in attr_list:
        setattr(event_obj, attr, np.delete((getattr(event_obj, attr)), idx_arr, 0))

def quality_cut(event_obj, event_num = False, var_names: tuple = ("purity", "completeness", "reco_num_hits_w"),
                reqs: tuple = (0.8, 0.8, 15)) -> None:
    #check if all variable names are valid and each variable has a valid requirement
    if all(var in dir(event_obj) for var in var_names) and len(var_names) == len(reqs):
        indices = np.array([])
        #first add indices where hit arrays are empty
        empty_mask = [np.any(i) for i in event_obj.reco_hits_x_w]
        indices = np.append(indices, [[i for i,val in enumerate(empty_mask) if not val]])
        
        if not event_num:
            #get indices where requirements are not met and pick out the unique indices
            for idx, attr in enumerate(var_names):
                indices = np.append(indices, np.where(getattr(event_obj, attr) < reqs[idx])[0])
            indices = np.unique(np.int64(indices))
            
            #del particles with these indices
            _delete_particles(event_obj, indices)
          
        else:
            #do same but only for records in a particular event_obj
            event_idxs = np.where(event_obj.event_number == event_num)
            for idx, attr in enumerate(var_names):
                np.concatenate(np.where(getattr(event_obj, attr)[event_idxs[0]:(event_idxs[-1]+1)] < reqs[idx])[0], indices)
            indices = np.unique(np.int64(indices))
            
            _delete_particles(event_obj, indices)
          
    else:
        raise RuntimeError("Variable names are invalid and/or each variable does not have a requirement")
    