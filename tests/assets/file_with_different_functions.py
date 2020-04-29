# import os


# ENTRY = "entry"

# long_str = """This is a long string

# With a looooooooooooottttttttt of characters


# Hoooooooooo
# """


# def parent(num) :
#     def first_child():
#         """
#         This is first child
#         """
#         return "Hi, I am Emma"

#     def second_child():
#         """
#         This is second child
#         """
#         for i in range(10):
#             print(i)

#         return "Call me Liam"

#     if num == 1:
#         return first_child
#     else:
#         return second_child
    

# def my_decorator(func):
#     """
#     Outer decorator function
#     """
#     def wrapper():
#         print("Something is happening before the function is called.")
#         func()
#         print("Something is happening after the function is called.")
#     return wrapper


# @my_decorator
# def say_whee():
#     """
#     Hellooooooooo

#     This is a function with decorators
#     """
#     print("Whee!")



# class BaseClass(object):

#     def __init__(self, x):
#         self.x = x
#         self.name = "BaseClass"

#     def get_name(self):
#         '''Get the name parameter
#         '''
#         return self.name
    
#     @property
#     def jj(self, x):
#         def scan(children):
#             print(children)
#         return x * x


def delete_comps_that_improve_ELBO(Data, model, Korig=0, LP=None,
                                   SS=None, ELBO=None, **kwargs):
  if LP is None:
    LP = model.calc_local_params(Data)
  if SS is None:
    SS = model.get_global_suff_stats(Data, LP, doPrecompEntropy=True)
  if ELBO is None:
    ELBO = model.calc_evidence(SS=SS)

  ''' Iteratively attempt deleting comps Kall, Kall-1, Kall-2, ... Korig
        going in this order makes it easiest to remove components
  '''
  K = SS.K
  for k in reversed(range(Korig, K)):
    rmodel = model.copy()
    rSS = SS.copy()
    rSS.removeComp(k)
    rmodel.obsModel.K = rSS.K
    rmodel.allocModel.update_global_params(rSS, mergeCompB=k)
    del rmodel.obsModel.comp[k]

    rLP = rmodel.calc_local_params(Data)
    rSS = rmodel.get_global_suff_stats(Data, rLP, doPrecompEntropy=True)
    rELBO = rmodel.calc_evidence(SS=rSS)

    if kwargs['doVizBirth'] == 3:
      viz_deletion_sidebyside(model, rmodel, ELBO, rELBO)

    if rELBO >= ELBO:
      SS = rSS
      LP = rLP
      model = rmodel
      ELBO = rELBO      
  return model, LP, SS, ELBO